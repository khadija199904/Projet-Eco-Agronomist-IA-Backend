from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

class TreatmentRAGBase(BaseModel):
    nom_maladie: str
    ordonnance: str
    sources_utilisees: Optional[str] = None

class TreatmentRAGCreate(TreatmentRAGBase):
    diagnostic_id: int

class TreatmentRAGResponse(TreatmentRAGBase):
    id: int
    diagnostic_id: int
    date_creation: datetime


    model_config = ConfigDict(from_attributes=True)