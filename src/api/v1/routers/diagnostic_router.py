from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.diagnostic_schema import (
    PlantDiagnosticCreate, PlantDiagnosticResponse, 
    DiagnosticProductCreate, DiagnosticProductResponse
)
from src.api.v1.crud import diagnostic_crud
from src.api.v1.services.diagnostic_service import diagnostic_service
from src.database.models.users import User
from src.database.models.enums import UserRole

router = APIRouter(prefix="/diagnostics-plante", tags=["Production - IA Diagnostic"])

@router.post("/", response_model=PlantDiagnosticResponse)
async def enregistrer_diagnostic_ia(
    lot_recolte_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Reçoit une photo du champ, exécute l'IA (YOLO) et enregistre le résultat.
    """
    if user.role != UserRole.AGRICULTEUR:
        raise HTTPException(status_code=403, detail="Réservé aux agriculteurs.")
    
    try:
        image_path = await diagnostic_service.save_upload_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de sauvegarde fichier : {e}")

    disease, severity, advice = diagnostic_service.run_prediction(image_path)

    diagnostic_create = PlantDiagnosticCreate(
        lot_recolte_id=lot_recolte_id,
        disease_detected=disease,
        severity_level=severity,
        treatment_advice=advice,
        treatments=[]
    )
    
    nouveau_diagnostic = diagnostic_crud.create_plant_diagnostic(db=db, diagnostic=diagnostic_create)
    
    
    return nouveau_diagnostic


@router.post("/valorisation", response_model=DiagnosticProductResponse)
async def enregistrer_diagnostic_valorisation(
    lot_recolte_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Diagnostic Qualité Station : Analyse le lot via IA pour le tri/emballage.
    """
    if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Réservé aux contrôleurs qualité.")
    
    # 1. Sauvegarde de l'image
    try:
        image_path = await diagnostic_service.save_upload_file(file, sub_dir="valorisation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de sauvegarde : {e}")

    # 2. IA Valorisation
    defects, score, taux, decision = diagnostic_service.run_valorisation_prediction(image_path)

    # 3. Création schema
    diag_create = DiagnosticProductCreate(
        lot_recolte_id=lot_recolte_id,
        image_url=image_path,
        visual_defects=defects,
        healthy_score=score,
        taux_defauts_visuels=taux,
        decision_flux=decision
    )

    # 4. Sauvegarde
    return diagnostic_crud.create_diagnostic_product(db, diag_create)


@router.get("/valorisation/lot/{lot_id}", response_model=List[DiagnosticProductResponse])
def historique_qualite_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role not in [UserRole.QUALITE, UserRole.ADMIN, UserRole.AGRICULTEUR]:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")
        
    return diagnostic_crud.get_diagnostic_products_by_lot(db, lot_id)


@router.get("/lot/{lot_id}", response_model=List[PlantDiagnosticResponse])
def historique_maladies_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    roles_autorises = [UserRole.AGRICULTEUR, UserRole.QUALITE, UserRole.ADMIN]
    if user.role not in roles_autorises:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")
        
    return diagnostic_crud.get_diagnostics_by_lot(db=db, lot_id=lot_id)
