from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.database.models.users import User
from src.database.models.enums import UserRole, DiagnosticType
from src.api.v1.schemas.diagnostic_schema import (
    ProductDiagnosticCreate
)
from src.api.v1.schemas.valorisation_schema import (
    TraitementStationCreate, TraitementStationResponse, 
    QualiteCheckResult, LotQualityReport, TraitementStationUpdate
)
from src.api.v1.crud import valorisation_crud, diagnostic_crud
from src.api.v1.services import diagnostic_service
from src.database.models.diagnostics_table import UniversalDiagnostic

router = APIRouter()

@router.post("/check", response_model=QualiteCheckResult)
async def check_quality(
    lot_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Analyse IA rapide d'un échantillon (inspiré de qualite.py)."""
    if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Accès réservé au contrôle qualité.")

    # 1. Sauvegarde et Inférence
    image_path = await diagnostic_service.save_upload_file(file, sub_dir="valorisation")
    defects, score, taux, decision, detection_details = diagnostic_service.run_valorisation_prediction(image_path)

    # 2. Enregistrement automatique du scan dans l'historique diagnostic
    diag_create = ProductDiagnosticCreate(
        lot_recolte_id=lot_id,
        image_url=image_path,
        visual_defects=defects,
        healthy_score=score,
        taux_defauts_visuels=taux,
        decision_flux=decision,
        detection_details=detection_details
    )
    diagnostic_crud.create_diagnostic_product(db, diag_create)

    return QualiteCheckResult(
        lot_id=lot_id,
        taux_conformite=round(score * 100, 2),
        defauts_detectes=defects,
        decision_suggeree=decision,
        image_url=image_path
    )

@router.get("/report/{lot_id}", response_model=LotQualityReport)
def get_quality_report(
    lot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Génère un rapport de synthèse basé sur tous les scans du lot."""
    scans = db.query(UniversalDiagnostic).filter(
        UniversalDiagnostic.lot_recolte_id == lot_id,
        UniversalDiagnostic.diag_type == DiagnosticType.PRODUCT
    ).all()
    if not scans:
        raise HTTPException(status_code=404, detail="Aucun scan trouvé pour ce lot.")

    avg_score = sum(s.healthy_score for s in scans) / len(scans)
    
    all_defects = {}
    for s in scans:
        if s.visual_defects:
            for defect, count in s.visual_defects.items():
                all_defects[defect] = all_defects.get(defect, 0) + count

    # On vérifie si une décision finale a déjà été prise
    traitement = db.query(valorisation_crud.TraitementStation).filter(valorisation_crud.TraitementStation.lot_recolte_id == lot_id).order_by(valorisation_crud.TraitementStation.date_agreage.desc()).first()

    return LotQualityReport(
        lot_id=lot_id,
        nb_scans=len(scans),
        taux_conformite_moyen=round(avg_score * 100, 2),
        defauts_frequents=all_defects,
        decision_finale=traitement.decision_flux if traitement else None,
        is_finalized=traitement.is_export if traitement else False,
        date_rapport=datetime.utcnow()
    )

@router.put("/finalize/{lot_id}", response_model=TraitementStationResponse)
def finalize_lot(
    lot_id: int,
    update_data: TraitementStationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Finalise la décision de traitement pour un lot."""
    if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Accès réservé au contrôle qualité.")
    
    return valorisation_crud.update_traitement_station(db, lot_id, update_data.model_dump())
