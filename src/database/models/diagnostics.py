from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base
import datetime
import enum

# ---  L'IA AU PÔLE PRODUCTION (Ferme) ---
class PlantDiagnostic(Base):
    """Diagnostic IA (Yolo) aux champs (Maladies des plantes)"""
    __tablename__ = 'plant_diagnostics'
    
    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey('lots_recolte.id'))
    
    # Résultat Scanner Yolo
    image_url = Column(String(255), nullable=True) # Photo prise par l'agriculteur
    disease_detected = Column(String(100))
    severity_level = Column(String(20))
    treatment_advice = Column(String(500)) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # La plante est malade
    treatments = relationship("Treatment", back_populates="diagnostic", cascade="all, delete-orphan")


class Treatment(Base):
    """Les produits appliqués SUITE à un PlantDiagnostic (Ferme)"""
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("plant_diagnostics.id"), nullable=False)
    
    product_used = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    dar_days = Column(Integer, nullable=True)
    
    diagnostic = relationship("PlantDiagnostic", back_populates="treatments")


# --- L'IA AU PÔLE VALORISATION (Station de conditionnement) ---
class DiagnosticProduct(Base):
    """
    Diagnostic IA (Yolo/Computer Vision) AVANT emballage.
    Caméra au-dessus du tapis roulant (Tri optique).
    """
    __tablename__ = 'diagnostic_products'
    
    id = Column(Integer, primary_key=True)
    lot_recolte_id = Column(Integer, ForeignKey('lots_recolte.id'))
    
    # Résultat Scanner Yolo
    image_url = Column(String(255), nullable=True) # Photo du tapis/produit
    visual_defects = Column(JSON) # JSON des bounding boxes YOLO/Anomalies
    healthy_score = Column(Float) # Score de qualité global 
    taux_defauts_visuels = Column(Float) # % de produits abîmés
    
    # Décision de la Station
    decision_flux = Column(String(50)) # 'MECANIQUE' ou 'DIRECT_EMBALLAGE'
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# --- L'IA AU PÔLE CONSOMMATION (Client PWA/Mobile) ---
class ConsumerDiagnostic(Base):
    """
    Diagnostic IA (Yolo) fait par un consommateur chez lui
    pour vérifier la fraîcheur d'un fruit avant achat ou ingestion.
    """
    __tablename__ = 'consumer_diagnostics'
    
    id = Column(Integer, primary_key=True)
    produit_fini_id = Column(Integer, ForeignKey('produits_finis.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Le consommateur (Optionnel)
    
    user = relationship("User", back_populates="diagnostics")
    
    # Résultat Scanner Yolo App Mobile
    image_url = Column(String(255), nullable=True) # Photo prise par le smartphone
    freshness_score = Column(Float) # Score de fraîcheur (0 à 1)
    is_edible = Column(Boolean, default=True) # Est-ce consommable ?
    defects_found = Column(JSON) # Ex: {"taches_noires": 2, "moisissure": 0}
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
