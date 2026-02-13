from sqlalchemy import Column, Integer, String,Float, ForeignKey, DateTime,Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base
import datetime


class PlantDiagnostic(Base):
    """Diagnostic IA sur plants avant ou pendant la récolte"""
    __tablename__ = 'plant_diagnostics'
    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey('lots_recolte.id'))
    
    # IA Vision (MobileNet) & LLM
    disease_detected = Column(String(100))
    severity_level = Column(String(20))
    treatment_advice = Column(String(500)) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)




class DiagnosticProduct(Base):
    """
    Diagnostic AVANT emballage (Agréage / Contrôle Qualité).
    C'est ici que l'IA décide du flux de production.
    """
    __tablename__ = 'diagnostic_products'
    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey('lots_recolte.id'))
    
    # --- Sortie du modèle IA (Vision/Scoring) ---
    visual_defects = Column(JSON) # Détails des anomalies
    healthy_score = Column(Float) 
    taux_defauts_visuels = Column(Float) # % de produits abîmés détectés
    
    # --- Décision Automatisée ---
    # Si healthy_score < 0.7 -> 'MECANIQUE' (Pré-tri), sinon 'DIRECT_EMBALLAGE'
    decision_flux = Column(String(50)) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"), nullable=False)
    product_used = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    dar_days = Column(Integer, nullable=True) # Delai Avant Recolte in days

    diagnostic = relationship("Diagnostic", backref="treatments")
