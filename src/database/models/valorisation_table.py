from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from src.database.database import Base



class TraitementStation(Base):
    """
    Gestion simplifiée : De l'agréage IA à la décision d'export.
    """
    __tablename__ = "traitements_station"

    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey("lots_recolte.id"))
    
    # --- Diagnostic & Qualité (Agréage) ---
    date_agreage = Column(DateTime)
    score_homogeneite = Column(Float)  
    besoin_tri_mecanique = Column(Boolean) 
    
    # --- Mesures Physico-Chimiques ---
    calibre = Column(String(20)) 
    
    # --- Résultat & Logistique ---
    poids_ecart = Column(Float)  
    is_export = Column(Boolean, default=False) 
