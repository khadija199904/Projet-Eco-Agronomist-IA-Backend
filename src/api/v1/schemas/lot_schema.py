from pydantic import BaseModel, ConfigDict
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

class LotRecolteUpdate(BaseModel):
    num_BL: Optional[str] = None
    produit_nom: Optional[str] = None
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    nombre_unit_transport: Optional[int] = None
    ferme_id: Optional[int] = None

class LotRecolteResponse(LotRecolteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code_qr_initial: str
    date_recolte: datetime
    agriculteur_id: int
