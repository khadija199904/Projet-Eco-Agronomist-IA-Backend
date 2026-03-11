from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from .ordonnance_schema import TreatmentCreate, TreatmentRAGResponse


class DetectionDetail(BaseModel):
    """Unified structure for IA detection results"""
    label: str
    confidence: float
    bbox: Optional[List[float]] = None
    status: str = "detected"


# --- 1. POLE PRODUCTION (Ferme) ---
class PlantDiagnosticBase(BaseModel):
    organization_id: int
    image_url: Optional[str] = None
    disease_detected: Optional[str] = None
    treatment_advice: Optional[str] = None
    detection_details: Optional[Dict[str, Any]] = None 

class PlantDiagnosticCreate(PlantDiagnosticBase):
    treatments: Optional[List[TreatmentCreate]] = []



class PlantDiagnosticResponse(PlantDiagnosticBase):
    id: int
    created_at: datetime
    treatments: List[TreatmentResponse] = []
    treatment_rag: Optional[TreatmentRAGResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- 2. POLE VALORISATION (Station) ---
class ProductDiagnosticBase(BaseModel):
    organization_id: int
    lot_recolte_id: int
    image_url: Optional[str] = None
    visual_defects: Optional[Dict[str, Any]] = None 
    healthy_score: Optional[float] = None
    taux_defauts_visuels: Optional[float] = None
    decision_flux: Optional[str] = None # 'MECANIQUE' ou 'DIRECT_EMBALLAGE'
    detection_details: Optional[Dict[str, Any]] = None

class ProductDiagnosticCreate(ProductDiagnosticBase):
    pass

class ProductDiagnosticResponse(ProductDiagnosticBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- 3. POLE CONSOMMATION (Client) ---
class ConsumerDiagnosticBase(BaseModel):
    produit_fini_id: Optional[int] = None
    user_id: Optional[int] = None
    image_url: Optional[str] = None
    freshness_score: Optional[float] = None
    is_edible: bool = True
    defects_found: Optional[Dict[str, Any]] = None

class ConsumerDiagnosticCreate(ConsumerDiagnosticBase):
    pass

class ConsumerDiagnosticResponse(ConsumerDiagnosticBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- GLOBAL / HISTORY ---
class DiagnosticHistoryItem(BaseModel):
    id: int
    diag_type: str # 'plante', 'valorisation', 'consommation'
    label: str
    confidence: float
    lot_recolte_id: Optional[int] = None
    organization_id: Optional[int] = None
    created_at: datetime

class DiagnosticListResponse(BaseModel):
    total: int
    diagnostics: List[DiagnosticHistoryItem]
