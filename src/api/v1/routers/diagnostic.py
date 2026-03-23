from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.diagnostic_schema import (
    PlantDiagnosticCreate, PlantDiagnosticResponse, 
    ProductDiagnosticCreate, ProductDiagnosticResponse,
    DiagnosticListResponse, DiagnosticHistoryItem,
    TreatmentRAGResponse,
    ConsumerDiagnosticCreate, ConsumerDiagnosticResponse
)

from src.api.v1.crud import diagnostic_crud, lot_crud, rag_crud

from src.api.v1.services import diagnostic_service
from src.database.models.users import User
from src.database.models.enums import UserRole, DiagnosticType
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.core.security import verify_token


router = APIRouter()

@router.post("/plant", response_model=PlantDiagnosticResponse)
async def diagnose_plant_disease(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
     ):
    if user.role != UserRole.AGRICULTEUR:
        raise HTTPException(status_code=403, detail="Accès réservé aux agriculteurs.")

    org_id = user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="L'utilisateur n'est rattaché à aucune organisation.")

    image_bytes = await file.read()
    disease_fr, det_details, pathologies_fr, image_path = diagnostic_service.run_plant_prediction(image_bytes)

        
    diag_create = PlantDiagnosticCreate(
        organization_id=org_id,
        image_url=image_path,
        disease_detected=disease_fr,
        detection_details=det_details
    )
    
    return diagnostic_crud.create_plant_diagnostic(db, diag_create)


@router.post("/{diagnostic_id}/ordonnance", response_model=TreatmentRAGResponse)
async def get_ordonnance_ia(
    diagnostic_id: int,
    culture: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Génère une ordonnance IA (RAG) à la demande pour un diagnostic existant.
    """
    # 1. Vérifier si le diagnostic existe
    diag = diagnostic_crud.get_plant_diagnostic_by_id(db, diagnostic_id)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnostic introuvable.")

    # 2. Extraire les pathologies (depuis les détails stockés)
    pathologies = diag.detection_details.get("pathologies", [])
    if not pathologies:
        # Fallback sur le label principal si pas de liste
        pathologies = [diag.disease_detected] if diag.disease_detected else []

    try:
        # 3. Appel du service RAG
        advice_text = await diagnostic_service.get_rag_ordonnance(pathologies, culture=culture)
        
        # 4. Sauvegarder dans la table RAG
        return rag_crud.create_treatment_rag(
            db, 
            diagnostic_id=diagnostic_id,
            nom_maladie=diag.disease_detected or "Inconnue",
            ordonnance=advice_text,
            sources="RAG Assistant (ONSSA Knowledge)"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")



@router.post("/product", response_model=ProductDiagnosticResponse)
async def valorize_product(
    lot_recolte_id: int = Form(..., description="ID du lot à analyser"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Sécurité : Rôle Qualité ou Admin
    if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Réservé aux contrôleurs qualité.")
    
    org_id = user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="L'utilisateur n'est rattaché à aucune organisation.")

    
    lot = lot_crud.get_lot_by_id(db, lot_recolte_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot de récolte introuvable.")

    # Lecture des bytes
    image_bytes = await file.read()
    defects, score, taux, decision, detection_details, annotated_path = diagnostic_service.run_valorisation_prediction(image_bytes)
    
    diag_create = ProductDiagnosticCreate(
        lot_recolte_id=lot_recolte_id,
        organization_id=org_id,
        image_url=annotated_path,
        visual_defects=defects,
        healthy_score=score,
        taux_defauts_visuels=taux,
        decision_flux=decision,
        detection_details=detection_details
    )
    return diagnostic_crud.create_diagnostic_product(db, diag_create)

@router.post("/consume", response_model=ConsumerDiagnosticResponse)
async def diagnose_consumer_product(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Diagnostic de fraîcheur direct via upload d'image.
    """
    # 1. Inférence IA (OpenCV + YOLO)
    image_bytes = await file.read()
    label_fr, confidence, det_details, image_path = diagnostic_service.run_freshness_prediction(image_bytes)

    # 2. Préparation du schéma de création
    diag_data = ConsumerDiagnosticCreate(
        user_id=user.id,
        image_url=image_path,
        freshness_score=confidence,
        is_edible=(label_fr == "Frais"),
        detection_details=det_details
    )

    # 3. Appel du CRUD pour sauvegarde (sans QR code)
    return diagnostic_crud.create_consumer_diagnostic(db, diag_data)
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
    
    if user.role != UserRole.CONSOMMATEUR and user.organization_id:
        query = query.filter(UniversalDiagnostic.organization_id == user.organization_id)
    
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
