from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TraitementStationBase(BaseModel):
    lot_recolte_id: int
    score_homogeneite: float
    besoin_tri_mecanique: bool
    calibre: Optional[str] = None
    poids_ecart: Optional[float] = 0.0
    is_export: bool = False

class TraitementStationCreate(TraitementStationBase):
    date_agreage: Optional[datetime] = None

class TraitementStationResponse(TraitementStationBase):
    id: int
    date_agreage: datetime

    class Config:
        from_attributes = True

class TraitementStationUpdate(BaseModel):
    besoin_tri_mecanique: Optional[bool] = None
    calibre: Optional[str] = None
    poids_ecart: Optional[float] = None
    is_export: Optional[bool] = None

class QualiteCheckResult(BaseModel):
    lot_id: int
    taux_conformite: float
    defauts_detectes: Dict[str, int]
    decision_suggeree: str # 'DIRECT_EMBALLAGE' ou 'MECANIQUE'
    image_url: Optional[str] = None

class LotQualityReport(BaseModel):
    lot_id: int
    nb_scans: int
    taux_conformite_moyen: float
    defauts_frequents: Dict[str, int]
    decision_finale: Optional[str] = None
    is_finalized: bool = False
    date_rapport: datetime
