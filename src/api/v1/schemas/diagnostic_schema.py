from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .ordonnance_schema import TreatmentCreate, TreatmentResponse


class DetectionResultDetail(BaseModel):
    label: str
    confidence: float
    status: str = "detected"


# --- Schémas pour le Diagnostic de la plante ---
class PlantDiagnosticBase(BaseModel):
    lot_recolte_id: int
    disease_detected: Optional[str] = None
    treatment_advice: Optional[str] = None
    detection_details: Optional[Dict[str, Any]] = None 

class PlantDiagnosticCreate(PlantDiagnosticBase):
    treatments: Optional[List[TreatmentCreate]] = []

class PlantDiagnosticResponse(PlantDiagnosticBase):
    id: int
    created_at: datetime
    treatments: List[TreatmentResponse] = []

    class Config:
        from_attributes = True

# --- Schémas pour le Diagnostic Qualité (Valorisation / Station) ---
class DiagnosticProductBase(BaseModel):
    lot_recolte_id: int
    image_url: Optional[str] = None
    visual_defects: Optional[Dict[str, Any]] = None 
    healthy_score: Optional[float] = None
    taux_defauts_visuels: Optional[float] = None
    decision_flux: Optional[str] = None # 'MECANIQUE' ou 'DIRECT_EMBALLAGE'
    detection_details: Optional[Dict[str, Any]] = None

class DiagnosticProductCreate(DiagnosticProductBase):
    pass

class DiagnosticHistoryItem(BaseModel):
    id: int
    diag_type: str # 'plante' or 'valorisation'
    label: str
    confidence: float
    lot_recolte_id: Optional[int]
    created_at: datetime

class DiagnosticListResponse(BaseModel):
    total: int
    diagnostics: List[DiagnosticHistoryItem]

class DiagnosticProductResponse(DiagnosticProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
