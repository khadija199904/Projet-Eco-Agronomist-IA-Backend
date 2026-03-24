from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_agreage: datetime

class TraitementStationUpdate(BaseModel):
    besoin_tri_mecanique: Optional[bool] = None
    calibre: Optional[str] = None
    poids_ecart: Optional[float] = None
    is_export: Optional[bool] = None

class QualiteCheckResult(BaseModel):
    lot_id: int
    taux_conformite: float
    defauts_detectes: dict[str, int]
    decision_suggeree: str # 'DIRECT_EMBALLAGE' ou 'MECANIQUE'
    image_url: Optional[str] = None

class LotQualityReport(BaseModel):
    lot_id: int
    nb_scans: int
    taux_conformite_moyen: float
    defauts_frequents: dict[str, int]
    decision_finale: Optional[str] = None
    is_finalized: bool = False
    date_rapport: datetime


# --- RECEPTION STATION ---
class ReceptionStationBase(BaseModel):
    lot_recolte_id: int
    poids_reception: float
    etat_initial: str

class ReceptionStationCreate(ReceptionStationBase):
    pass

class ReceptionStationResponse(ReceptionStationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_reception: datetime
    receptionnaire_id: int
