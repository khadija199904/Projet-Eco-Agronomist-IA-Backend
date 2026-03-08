from sqlalchemy.orm import Session
from src.database.models.diagnostics import PlantDiagnostic, Treatment
from src.api.v1.schemas.diagnostic_schema import PlantDiagnosticCreate, TreatmentCreate

def create_plant_diagnostic(db: Session, diagnostic: PlantDiagnosticCreate):
    # "treatments" n'est pas une colonne de la db, c'est une relation
    diagnostic_data = diagnostic.model_dump(exclude={"treatments"})
    
    #  Création du diagnostic
    nouveau_diag = PlantDiagnostic(**diagnostic_data)
    db.add(nouveau_diag)
    db.commit()
    db.refresh(nouveau_diag)
    
    # 3. S'il y a des traitements spécifiés en même temps, on les crée aussi
    if diagnostic.treatments:
        for t in diagnostic.treatments:
            nouveau_traitement = Treatment(
                diagnostic_id=nouveau_diag.id,
                **t.model_dump()
            )
            db.add(nouveau_traitement)
        db.commit()
        db.refresh(nouveau_diag) # Pour que la relation soit mise à jour dans l'objet Python
        
    return nouveau_diag

def get_diagnostics_by_lot(db: Session, lot_id: int):
    # On récupère tous les diagnostics d'un lot spécifique
    return db.query(PlantDiagnostic).filter(PlantDiagnostic.lot_recolte_id == lot_id).all()
