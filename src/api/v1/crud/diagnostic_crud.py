from sqlalchemy.orm import Session
from src.database.models.diagnostics_table import UniversalDiagnostic
from src.database.models.ordonnacesIA import TreatmentRAG
from src.database.models.enums import DiagnosticType
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate, ProductDiagnosticCreate, ConsumerDiagnosticCreate

def create_plant_diagnostic(db: Session, diagnostic: PlantDiagnosticCreate):
    diagnostic_data = diagnostic.model_dump(exclude={"treatments"})
    
    nouveau_diag = UniversalDiagnostic(
        diag_type=DiagnosticType.PLANT,
        **diagnostic_data
    )
    db.add(nouveau_diag)
    db.commit()
    db.refresh(nouveau_diag)
    
    if diagnostic.treatments:
        for t in diagnostic.treatments:
            nouveau_traitement = TreatmentRAG(
                diagnostic_id=nouveau_diag.id,
                **t.model_dump()
            )
            db.add(nouveau_traitement)
        db.commit()
        db.refresh(nouveau_diag) 
        
    return nouveau_diag

def get_diagnostics_by_organization(db: Session, org_id: int, diag_type: DiagnosticType = None):
    query = db.query(UniversalDiagnostic).filter(
        UniversalDiagnostic.organization_id == org_id
    )
    if diag_type:
        query = query.filter(UniversalDiagnostic.diag_type == diag_type)
    
    return query.order_by(UniversalDiagnostic.created_at.desc()).all()

def get_plant_diagnostic_by_id(db: Session, diagnostic_id: int):
    diag = db.get(UniversalDiagnostic, diagnostic_id)
    if diag and diag.diag_type != DiagnosticType.PLANT:
        return None
    return diag

def create_diagnostic_product(db: Session, diagnostic: ProductDiagnosticCreate):
    nouveau_diag = UniversalDiagnostic(
        diag_type=DiagnosticType.PRODUCT,
        **diagnostic.model_dump()
    )
    db.add(nouveau_diag)
    db.commit()
    db.refresh(nouveau_diag)
    return nouveau_diag

def get_diagnostic_products_by_lot(db: Session, lot_id: int):
    return db.query(UniversalDiagnostic).filter(
        UniversalDiagnostic.lot_recolte_id == lot_id,
        UniversalDiagnostic.diag_type == DiagnosticType.PRODUCT
    ).all()

def get_product_diagnostic_by_id(db: Session, diagnostic_id: int):
    diag = db.get(UniversalDiagnostic, diagnostic_id)
    if diag and diag.diag_type != DiagnosticType.PRODUCT:
        return None
    return diag



def create_consumer_diagnostic(db: Session, obj_in: ConsumerDiagnosticCreate):
    """
    Crée un diagnostic de consommation sans recherche de produit fini.
    """
    db_obj = UniversalDiagnostic(
        diag_type=DiagnosticType.CONSUMER,
        user_id=obj_in.user_id,
        image_url=obj_in.image_url,
        freshness_score=obj_in.freshness_score,
        is_edible=obj_in.is_edible,
        detection_details=obj_in.detection_details,
        disease_detected="Frais" if obj_in.is_edible else "Pourri"
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_consumer_diagnostics_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(UniversalDiagnostic)\
             .filter(UniversalDiagnostic.diag_type == DiagnosticType.CONSUMER, 
                     UniversalDiagnostic.user_id == user_id)\
             .offset(skip).limit(limit).all()