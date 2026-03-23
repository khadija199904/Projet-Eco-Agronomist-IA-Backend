from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.diagnostic_schema import TreatmentRAGResponse
from src.api.v1.crud import diagnostic_crud
from src.api.v1.services import diagnostic_service
from src.database.models.users import User

router = APIRouter()

@router.post("/production/{diagnostic_id}/get-treatment", response_model=TreatmentRAGResponse)
async def get_diagnostic_ordonnance(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    
    diagnostic = diagnostic_crud.get_plant_diagnostic(db, diagnostic_id)
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic cette plante est introuvable,Rescanez cette feuille ")
    try:
        
        culture = None
        if diagnostic.detection_details:
            culture = diagnostic.detection_details.get("culture")
            
        pathologies = [diagnostic.disease_detected]
        ordonnance = await diagnostic_service.get_rag_ordonnance(pathologies, culture)
        
        updated_diag = diagnostic_crud.update_plant_treatment(db, diagnostic_id, ordonnance)
        return updated_diag.treatment_advice
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du conseil")

