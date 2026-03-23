from sqlalchemy.orm import Session
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.database.models.ordonnacesIA import TreatmentRAG
from src.database.models.enums import DiagnosticType
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate, TreatmentRAGCreate, ProductDiagnosticCreate


def create_treatment_rag(db: Session, diagnostic_id: int, nom_maladie: str, ordonnance: str, sources: str = None):
    """
    Crée une nouvelle entrée TreatmentRAG liée à un diagnostic existant.
    """
    nouveau_traitement = TreatmentRAG(
        diagnostic_id=diagnostic_id,
        nom_maladie=nom_maladie,
        ordonnance=ordonnance,
        sources_utilisees=sources
    )
    db.add(nouveau_traitement)
    db.commit()
    db.refresh(nouveau_traitement)
    return nouveau_traitement

