from sqlalchemy.orm import Session
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.database.models.produit_fini import ProduitFini
from src.database.models.enums import DiagnosticType
from src.api.v1.schemas.diagnostic_schema import ConsumerDiagnosticCreate

def create_consumer_diagnostic(db: Session, obj_in: ConsumerDiagnosticCreate, code_qr: str):
    """
    Crée un diagnostic de consommation en reliant le scan au produit fini existant.
    """
    # 1. Récupération du produit fini via le code QR (ton identifiant texte)
    produit = db.query(ProduitFini).filter(ProduitFini.code_qr_final == code_qr).first()
    
    # 2. Préparation des données pour la table unifiée
    # On mappe les champs du schéma Consumer vers UniversalDiagnostic
    db_obj = UniversalDiagnostic(
        diag_type=DiagnosticType.CONSUMER,
        user_id=obj_in.user_id,
        produit_fini_id=produit.id if produit else None,
        organization_id=produit.station_id if produit else None,
        lot_recolte_id=produit.lot_recolte_id if produit else None,
        
        image_url=obj_in.image_url,
        healthy_score=obj_in.freshness_score,
        is_edible=obj_in.is_edible,
        detection_details=obj_in.defects_found,
        
        # On peut aussi stocker le label textuel pour l'historique
        disease_detected="Frais" if obj_in.is_edible else "Avarié"
    )

    db.add(db_obj)
    
    # 3. Mise à jour optionnelle du score sur le produit fini lui-même
    if produit:
        produit.score_qualite = obj_in.freshness_score
        produit.consommateur_id = obj_in.user_id

    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_consumer_diagnostics_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(UniversalDiagnostic)\
             .filter(UniversalDiagnostic.diag_type == DiagnosticType.CONSUMER, 
                     UniversalDiagnostic.user_id == user_id)\
             .offset(skip).limit(limit).all()