from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.database.models.organization_table import Organization
from src.api.v1.schemas.organization_schema import OrganizationCreate, OrganizationUpdate

def create_organization(db: Session, org_in: OrganizationCreate):
    new_org = Organization(**org_in.model_dump())
    try:
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        return new_org
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur d'intégrité : {str(e.orig)}"
        )

def get_organization(db: Session, org_id: int):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation introuvable")
    return org

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Organization).offset(skip).limit(limit).all()

def update_organization(db: Session, org_id: int, org_in: OrganizationUpdate):
    org = get_organization(db, org_id)
    update_data = org_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
    try:
        db.commit()
        db.refresh(org)
        return org
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mise à jour impossible")

def delete_organization(db: Session, org_id: int):
    org = get_organization(db, org_id)
    try:
        db.delete(org)
        db.commit()
        return {"message": "Organisation supprimée avec succès"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Impossible de supprimer cette organisation car elle est liée à des utilisateurs ou d'autres ressources.")
