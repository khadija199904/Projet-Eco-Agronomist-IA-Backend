from sqlalchemy.orm import Session
from src.database.models.diagnostics_table import PlantDiagnostic,TreatmentRAG, DiagnosticProduct
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate, TreatmentCreate, DiagnosticProductCreate

def create_plant_diagnostic(db: Session, diagnostic: PlantDiagnosticCreate):
    diagnostic_data = diagnostic.model_dump(exclude={"treatments"})
    
    nouveau_diag = PlantDiagnostic(**diagnostic_data)
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

def get_diagnostics_by_lot(db: Session, lot_id: int):
    return db.query(PlantDiagnostic).filter(PlantDiagnostic.lot_recolte_id == lot_id).all()

def get_plant_diagnostic_by_id(db: Session, diagnostic_id: int):
    return db.get(PlantDiagnostic, diagnostic_id)

def create_diagnostic_product(db: Session, diagnostic: DiagnosticProductCreate):
    nouveau_diag = DiagnosticProduct(**diagnostic.model_dump())
    db.add(nouveau_diag)
    db.commit()
    db.refresh(nouveau_diag)
    return nouveau_diag

def get_diagnostic_products_by_lot(db: Session, lot_id: int):
    return db.query(DiagnosticProduct).filter(DiagnosticProduct.lot_recolte_id == lot_id).all()

def get_product_diagnostic_by_id(db: Session, diagnostic_id: int):
    return db.get(DiagnosticProduct, diagnostic_id)
