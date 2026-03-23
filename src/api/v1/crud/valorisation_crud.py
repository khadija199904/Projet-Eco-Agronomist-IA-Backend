from sqlalchemy.orm import Session
from src.database.models.valorisation_table import TraitementStation, ReceptionStation
from src.api.v1.schemas.valorisation_schema import TraitementStationCreate, ReceptionStationCreate
from datetime import datetime

def create_traitement_station(db: Session, traitement: TraitementStationCreate):
    db_traitement = TraitementStation(
        **traitement.model_dump(exclude_none=True)
    )
    if not db_traitement.date_agreage:
        db_traitement.date_agreage = datetime.utcnow()
        
    db.add(db_traitement)
    db.commit()
    db.refresh(db_traitement)
    return db_traitement

def get_traitements_by_lot(db: Session, lot_id: int):
    return db.query(TraitementStation).filter(TraitementStation.lot_recolte_id == lot_id).all()

def update_traitement_station(db: Session, lot_id: int, data: dict):
    # On cherche le traitement le plus récent pour ce lot ou on en crée un
    traitement = db.query(TraitementStation).filter(TraitementStation.lot_recolte_id == lot_id).order_by(TraitementStation.date_agreage.desc()).first()
    
    if not traitement:
        traitement = TraitementStation(lot_recolte_id=lot_id, date_agreage=datetime.utcnow())
        db.add(traitement)
    
    for key, value in data.items():
        if value is not None:
            setattr(traitement, key, value)
            
    db.commit()
    db.refresh(traitement)
    return traitement


# --- RECEPTION CRUD ---
def create_reception(db: Session, reception: ReceptionStationCreate, receptionnaire_id: int):
    db_reception = ReceptionStation(
        **reception.model_dump(),
        receptionnaire_id=receptionnaire_id
    )
    db.add(db_reception)
    db.commit()
    db.refresh(db_reception)
    return db_reception

def get_reception_by_lot(db: Session, lot_id: int):
    return db.query(ReceptionStation).filter(ReceptionStation.lot_recolte_id == lot_id).first()

def get_all_receptions(db: Session):
    """Retourne toutes les réceptions enregistrées à la station."""
    return db.query(ReceptionStation).all()
