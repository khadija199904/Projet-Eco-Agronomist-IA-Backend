from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Schémas pour les Traitements ---
class TreatmentBase(BaseModel):
    product_used: str
    dosage: str
    dar_days: Optional[int] = None # Délai avant récolte peut être vide

class TreatmentCreate(TreatmentBase):
    pass

class TreatmentResponse(TreatmentBase):
    id: int
    diagnostic_id: int
    application_date: datetime

    class Config:
        from_attributes = True


# --- Schémas pour les détails de détection YOLO ---
class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float
    label: str

class DetectionResultDetail(BaseModel):
    label: str
    confidence: float
    boxes: List[BoundingBox]
    status: str = "detected"


# --- Schémas pour le Diagnostic de la plante ---
class PlantDiagnosticBase(BaseModel):
    lot_recolte_id: int
    disease_detected: Optional[str] = None
    severity_level: Optional[str] = None
    treatment_advice: Optional[str] = None
    detection_details: Optional[Dict[str, Any]] = None # Pour stocker les boxes et scores détaillés

class PlantDiagnosticCreate(PlantDiagnosticBase):
    # L'utilisateur de l'API peut directement passer une liste de traitements !
    treatments: Optional[List[TreatmentCreate]] = []

class PlantDiagnosticResponse(PlantDiagnosticBase):
    id: int
    created_at: datetime
    # On renvoie aussi les traitements associés à ce diagnostic (Relations imbriquées)
    treatments: List[TreatmentResponse] = []

    class Config:
        from_attributes = True

# --- Schémas pour le Diagnostic Qualité (Valorisation / Station) ---
class DiagnosticProductBase(BaseModel):
    lot_recolte_id: int
    image_url: Optional[str] = None
    visual_defects: Optional[Dict[str, Any]] = None # JSON des bounding boxes/anomalies
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
