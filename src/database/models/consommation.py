from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from src.database.database import Base

class ProduitFini(Base):
    """
    Le produit emballé avec son QR Code Final[cite: 32, 110].
    """
    __tablename__ = "produits_finis"

    id = Column(Integer, primary_key=True)
    traitement_id = Column(Integer, ForeignKey("traitements_station.id"), nullable=True)
    lot_recolte_id = Column(Integer, ForeignKey("lots_recolte.id"), nullable=True) # Traçabilité amont
    
    # --- Traçabilité Consommateur ---
    code_qr_final = Column(String(255), unique=True) # Scanné par le client [cite: 20]
    date_emballage = Column(DateTime, server_default=func.now())
    type_conditionnement = Column(String(100)) 
    
    consommateur_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    calibre = Column(String(50))
    station_id = Column(Integer, ForeignKey("organizations.id"))
    
    score_qualite = Column(Float)
    rapport_inspection_url = Column(String(255)) # [cite: 94, 103]