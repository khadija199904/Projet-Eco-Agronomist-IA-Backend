from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TreatmentBase(BaseModel):
    product_used: str
    dosage: str
    dar_days: Optional[int] = None 

class TreatmentCreate(TreatmentBase):
    pass

class TreatmentResponse(TreatmentBase):
    id: int
    diagnostic_id: int
    application_date: datetime

    class Config:
        from_attributes = True