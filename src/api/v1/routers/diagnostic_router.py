from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate, PlantDiagnosticResponse
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
