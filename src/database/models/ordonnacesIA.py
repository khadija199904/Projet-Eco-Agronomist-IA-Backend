from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.database import Base

class TreatmentRAG(Base):
    __tablename__ = "treatment_rag"

    id = Column(Integer, primary_key=True, index=True)
    
    # Lien avec le diagnostic de la plante
    diagnostic_id = Column(Integer, ForeignKey("universal_diagnostics.id"), nullable=False)
    
    # Ce que le RAG a trouvé
    nom_maladie = Column(String, nullable=False)  # ex: "Rouille du blé"
    recommandation = Column(Text, nullable=False) # L'ordonnance complète
    sources_utilisees = Column(String)            # ex: "ONSSA, Book Universel"
    
    # Infos automatiques
    date_creation = Column(DateTime, server_default=func.now())

    # Relation inverse vers le Diagnostic
    diagnostic = relationship("UniversalDiagnostic", back_populates="treatments")