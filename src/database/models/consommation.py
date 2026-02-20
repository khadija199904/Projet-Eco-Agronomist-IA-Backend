from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean ,func
from database.database import Base



class ProduitFini(Base):
    """
    Le produit emballé avec son QR Code Final[cite: 32, 110].
    """
    __tablename__ = "produits_finis"

    id = Column(Integer, primary_key=True)
    traitement_id = Column(Integer, ForeignKey("traitements_station.id"))
    
    # --- Traçabilité Consommateur ---
    code_qr_final = Column(String(255), unique=True) # Scanné par le client [cite: 20]
    date_emballage = Column(DateTime, server_default=func.now())
    type_conditionnement = Column(String(100)) 
    
    # Lien avec l'historique d'achat [cite: 22]
    consommateur_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class ProduitFini(Base):
    __tablename__ = "produits_finis"

    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey("lots_recolte.id")) # Traçabilité amont
    code_qr_final = Column(String(255), unique=True) # Scanné par le consommateur [cite: 20, 32]
    
    date_emballage = Column(DateTime, server_default=func.now())
    calibre = Column(String(50))
    station_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Résultats du contrôle qualité usine [cite: 83]
    score_qualite = Column(Float)
    rapport_inspection_url = Column(String(255)) # [cite: 94, 103]