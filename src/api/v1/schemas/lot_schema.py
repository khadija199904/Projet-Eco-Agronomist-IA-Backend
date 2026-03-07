from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LotRecolteBase(BaseModel):
    num_BL: str
    produit_nom: str
    poids_brut: float
    poids_net: float
    nombre_unit_transport: int
    ferme_id: int

class LotRecolteCreate(LotRecolteBase):
    pass 

class LotRecolteResponse(LotRecolteBase):
    id: int
    code_qr_initial: str
    date_recolte: datetime
    agriculteur_id: int

    class Config:
        from_attributes = True 
