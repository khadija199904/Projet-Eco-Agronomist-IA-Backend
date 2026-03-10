from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from src.database.database import Base
from sqlalchemy.orm import relationship

class LotRecolte(Base):
    """
    Représente le 'Lot de Récolte' généré par l'Agriculteur[cite: 37, 38].
    Intègre la paperasse technique de suivi.
    """
    __tablename__ = "lots_recolte"

    id = Column(Integer, primary_key=True)
    # --- Documents et Suivi (Paperasse Technique) ---
    num_BL = Column(String(50), unique=True) # Le 'Bon de Livraison' champ
    code_qr_initial = Column(String(255), unique=True) # QR généré au champ [cite: 38]
    
    # --- Données Physiques ---
    produit_nom = Column(String(100)) # ex: Tomate
    poids_brut = Column(Float) # Poids avec Pallox
    poids_net = Column(Float) # Poids marchandise seule
    nombre_unit_transport = Column(Integer) # Nombre de caisses/pallox
    
    date_recolte = Column(DateTime, server_default=func.now())
    agriculteur_id = Column(Integer, ForeignKey("users.id"))
    ferme_id = Column(Integer, ForeignKey("organizations.id"))

    agriculteur = relationship("User", foreign_keys=[agriculteur_id])
    ferme = relationship("Organization", foreign_keys=[ferme_id])