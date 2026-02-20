from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from database.database import Base



class TraitementStation(Base):
    """
    Gestion simplifiée : De l'agréage IA à la décision d'export.
    """
    __tablename__ = "traitements_station"

    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey("lots_recolte.id"))
    
    # --- Diagnostic & Qualité (Agréage) ---
    date_agreage = Column(DateTime)
    score_homogeneite = Column(Float)  # Issu de l'IA (0 à 1) : décide du flux
    besoin_tri_mecanique = Column(Boolean) # True si score faible (Fayaje complexe)
    
    # --- Mesures Physico-Chimiques ---
    brix = Column(Float)       # Taux de sucre
    fermete = Column(Float)    # Résistance (Pénétromètre)
    calibre = Column(String(20)) # Taille dominante
    
    # --- Résultat & Logistique ---
    poids_ecart = Column(Float)  # Quantité de déchets/écarts
    is_export = Column(Boolean, default=False) # Décision finale
    temp_froid = Column(Float)   # Température de pré-cooling