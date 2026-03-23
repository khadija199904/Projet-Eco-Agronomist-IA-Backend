from sqlalchemy.orm import Session
from src.database.models.production_table import LotRecolte
from src.api.v1.schemas.lot_schema import LotRecolteCreate
import uuid

def create_lot(db: Session, lot: LotRecolteCreate, agriculteur_id: int):
    # Génération du QR Code automatiquement 
    qr_code = f"QR-LOT-{uuid.uuid4().hex[:8].upper()}"
    
    nouveau_lot = LotRecolte(
        **lot.model_dump(),     
        code_qr_initial=qr_code,
        agriculteur_id=agriculteur_id
    )
    
    db.add(nouveau_lot)
    db.commit()
    db.refresh(nouveau_lot)
    return nouveau_lot

def get_lots_by_ferme(db: Session, ferme_id: int):
    # Retourne tous les lots liés à l'organisation de l'agriculteur
    return db.query(LotRecolte).filter(LotRecolte.ferme_id == ferme_id).all()

def get_lots(db: Session, skip: int = 0, limit: int = 100, ferme_id: int = None):
    query = db.query(LotRecolte)
    if ferme_id:
        query = query.filter(LotRecolte.ferme_id == ferme_id)
    return query.offset(skip).limit(limit).all()

def get_lot_by_id(db: Session, lot_id: int):
    return db.query(LotRecolte).filter(LotRecolte.id == lot_id).first()

def update_lot(db: Session, lot_id: int, lot_update: any):
    db_lot = get_lot_by_id(db, lot_id)
    if not db_lot:
        return None
        
    update_data = lot_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lot, key, value)
        
    db.commit()
    db.refresh(db_lot)
    return db_lot

def delete_lot(db: Session, lot_id: int):
    db_lot = get_lot_by_id(db, lot_id)
    if not db_lot:
        return False
        
    db.delete(db_lot)
    db.commit()
    return True
