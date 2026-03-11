from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TreatmentRAGBase(BaseModel):
    nom_maladie: str
    recommandation: str
    sources_utilisees: Optional[str] = None

class TreatmentRAGCreate(TreatmentRAGBase):
    diagnostic_id: int

class TreatmentRAGResponse(TreatmentRAGBase):
    id: int
    diagnostic_id: int
    date_creation: datetime


    model_config = ConfigDict(from_attributes=True)