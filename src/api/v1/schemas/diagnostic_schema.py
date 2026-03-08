from pydantic import BaseModel
from typing import Optional, List
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


# --- Schémas pour le Diagnostic de la plante ---
class PlantDiagnosticBase(BaseModel):
    lot_recolte_id: int
    disease_detected: Optional[str] = None
    severity_level: Optional[str] = None
    treatment_advice: Optional[str] = None

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
