from sqlalchemy.orm import Session
from src.database.models.production import LotRecolte
from src.api.v1.schemas.lot_schema import LotRecolteCreate
import uuid

def create_lot(db: Session, lot: LotRecolteCreate, agriculteur_id: int):
    # Génération du QR Code automatiquement 
    qr_code = f"QR-LOT-{uuid.uuid4().hex[:8].upper()}"
    
    nouveau_lot = LotRecolte(
        **lot.model_dump(),     # Assigne auto num_BL, produit_nom, poids... 
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
