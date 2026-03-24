from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from src.database.database import Base
from src.database.models.enums import DiagnosticType
import datetime

class UniversalDiagnostic(Base):
    """
    Table unique pour tous les diagnostics IA (Production, Valorisation, Consommation)
    """
    __tablename__ = 'universal_diagnostics'
    
    id = Column(Integer, primary_key=True)
    diag_type = Column(Enum(DiagnosticType), nullable=False)
    
    # --- Tracabilité (selon le pôle) ---
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True) # Pour Production
    lot_recolte_id = Column(Integer, ForeignKey('lots_recolte.id'), nullable=True) # Pour Valorisation
    produit_fini_id = Column(Integer, ForeignKey('produits_finis.id'), nullable=True) # Pour Consommation
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Le consommateur ou l'agent
    code_qr = Column(String(255), nullable=True) # Pour recherche directe sans table produit fini
    
    # --- Données Communes ---
    image_url = Column(String(255), nullable=True)
    detection_details = Column(JSON) # JSON brut des boîtes et labels YOLO
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # --- SPECIFIQUE PRODUCTION (Maladies) ---
    disease_detected = Column(String(100), nullable=True)
    treatment_advice = Column(String(500), nullable=True) 
    
    # --- SPECIFIQUE VALORISATION (Qualité station) ---
    visual_defects = Column(JSON, nullable=True) # Ex: {"taches": 5, "calibre_petit": 2}
    healthy_score = Column(Float, nullable=True) # Score global 0-1
    taux_defauts_visuels = Column(Float, nullable=True)
    decision_flux = Column(String(50), nullable=True) # 'MECANIQUE' ou 'DIRECT_EMBALLAGE'
    
    # --- SPECIFIQUE CONSOMMATION (Fraîcheur client) ---
    freshness_score = Column(Float, nullable=True)
    is_edible = Column(Boolean, default=True)
    
    # --- Relations ---
    user = relationship("User", back_populates="diagnostics")
    organization = relationship("Organization", back_populates="diagnostics")
    treatments = relationship("TreatmentRAG", back_populates="diagnostic", cascade="all, delete-orphan")
