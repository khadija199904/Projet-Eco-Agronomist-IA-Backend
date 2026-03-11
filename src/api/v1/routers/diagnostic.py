from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.diagnostic_schema import (
    PlantDiagnosticCreate, PlantDiagnosticResponse, 
    ProductDiagnosticCreate, ProductDiagnosticResponse,
    DiagnosticListResponse, DiagnosticHistoryItem
)
from src.api.v1.crud import diagnostic_crud
from src.api.v1.services import diagnostic_service
from src.database.models.users import User
from src.database.models.users import User
from src.database.models.enums import UserRole, DiagnosticType
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.core.security import verify_token
import json
import base64

router = APIRouter()

@router.post("/upload", summary="Analyser une image (Plante ou Produit)")
async def upload_and_diagnose(
    diag_type: str = Form(..., description="Type de diagnostic : 'plante' ou 'produit'"),
    organization_id: Optional[int] = Form(None),
    lot_recolte_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Analyse une image via IA. 
    """
    if diag_type in ["plante", "produit"]:
        if not organization_id or organization_id == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"L'identifiant de l'organisation est obligatoire pour le pôle {diag_type}."
            )
    
    else:
        organization_id = None
    

    if diag_type == "plante":
        if user.role != UserRole.AGRICULTEUR:
            raise HTTPException(status_code=403, detail="Réservé aux agriculteurs.")

        
        image_bytes = await file.read()
        disease, advice, detection_details = diagnostic_service.run_prediction(image_bytes)
        diag_create = PlantDiagnosticCreate(
            organization_id=organization_id,
            disease_detected=disease,
            treatment_advice=advice or "Aucun conseil disponible pour le moment.",
            detection_details=detection_details 
        )

        new_diagnostic = diagnostic_crud.create_plant_diagnostic(db, diag_create)
        
        return new_diagnostic
    elif diag_type == "produit":
        if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Réservé aux contrôleurs qualité.")
        
        try:
            image_path = await diagnostic_service.save_upload_file(file, sub_dir="valorisation")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur sauvegarde : {e}")

        defects, score, taux, decision, detection_details = diagnostic_service.run_valorisation_prediction(image_path)
        
        diag_create = ProductDiagnosticCreate(
            lot_recolte_id=lot_recolte_id,
            image_url=image_path,
            visual_defects=defects,
            healthy_score=score,
            taux_defauts_visuels=taux,
            decision_flux=decision,
            detection_details=detection_details
        )
        return diagnostic_crud.create_diagnostic_product(db, diag_create)
    
    else:
        raise HTTPException(status_code=400, detail="diag_type invalide. Utilisez 'plante' ou 'produit'.")


@router.get("/history", response_model=DiagnosticListResponse)
def get_history(
    diag_type: Optional[str] = None,
    lot_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Historique unifié des diagnostics."""
    authorized_roles = [UserRole.AGRICULTEUR, UserRole.QUALITE, UserRole.ADMIN, UserRole.CONSOMMATEUR]
    if user.role not in authorized_roles:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    query = db.query(UniversalDiagnostic)
    
    # Filtrage par pole / type
    if diag_type == "plante":
        query = query.filter(UniversalDiagnostic.diag_type == DiagnosticType.PLANT)
    elif diag_type in ["produit", "valorisation"]:
        query = query.filter(UniversalDiagnostic.diag_type == DiagnosticType.PRODUCT)
    elif diag_type == "consommation":
        query = query.filter(UniversalDiagnostic.diag_type == DiagnosticType.CONSUMER)

    # Filtrage par lot
    if user.role == UserRole.CONSOMMATEUR:
        query = query.filter(UniversalDiagnostic.user_id == user.id)

    results = query.order_by(UniversalDiagnostic.created_at.desc()).all()
    
    history = []
    for d in results:
        label = "Inconnu"
        if d.diag_type == DiagnosticType.PLANT:
            label = d.disease_detected or "Sain"
        elif d.diag_type == DiagnosticType.PRODUCT:
            label = "Qualité" if (d.healthy_score or 0) > 0.8 else "Défaut"
        elif d.diag_type == DiagnosticType.CONSUMER:
            label = "Comestible" if d.is_edible else "Non comestible"

        history.append(DiagnosticHistoryItem(
            id=d.id,
            diag_type=d.diag_type.value,
            label=label,
            confidence=d.healthy_score if d.diag_type == DiagnosticType.PRODUCT else 1.0, # Simplified
            lot_recolte_id=d.lot_recolte_id,
            organization_id=d.organization_id,
            created_at=d.created_at
        ))

    return DiagnosticListResponse(total=len(history), diagnostics=history)


@router.get("/{diag_type}/{diagnostic_id}")
def get_diagnostic_detail(
    diag_type: str,
    diagnostic_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Détail d'un diagnostic spécifique."""
    authorized_roles = [UserRole.AGRICULTEUR, UserRole.QUALITE, UserRole.ADMIN, UserRole.CONSOMMATEUR]
    if user.role not in authorized_roles:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    if diag_type == "plante":
        res = diagnostic_crud.get_plant_diagnostic_by_id(db, diagnostic_id)
    elif diag_type in ["produit", "valorisation"]:
        res = diagnostic_crud.get_product_diagnostic_by_id(db, diagnostic_id)
    else:
        # Pour consommation on peut rajouter un CRUD si besoin, ou utiliser le db.get direct
        res = db.get(UniversalDiagnostic, diagnostic_id)
        if res and res.diag_type != DiagnosticType.CONSUMER:
            res = None

    if not res:
        raise HTTPException(status_code=404, detail="Diagnostic introuvable")
    
    # Vérification propriété pour consommateur
    if user.role == UserRole.CONSOMMATEUR and res.user_id != user.id:
        raise HTTPException(status_code=403, detail="Accès refusé.")

    return res
