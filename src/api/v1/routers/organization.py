from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.organization_schema import (
    OrganizationCreate, OrganizationResponse, 
    OrganizationUpdate
)
from src.api.v1.crud import organization_crud
from src.database.models.users import User
from src.database.models.enums import UserRole

router = APIRouter()

@router.post("/", response_model=OrganizationResponse, status_code=201)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle organisation (Ferme ou Station de conditionnement).
    Access: public (ou modifiable pour Admin uniquement).
    """
    return organization_crud.create_organization(db, org_in)

@router.get("/", response_model=List[OrganizationResponse])
def read_organizations(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lister toutes les organisations existantes.
    """
    return organization_crud.get_organizations(db, skip=skip, limit=limit)

@router.get("/{org_id}", response_model=OrganizationResponse)
def read_organization(
    org_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'une organisation spécifique.
    """
    return organization_crud.get_organization(db, org_id)

@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: int,
    org_in: OrganizationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Mettre à jour une organisation.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs.")
        
    return organization_crud.update_organization(db, org_id, org_in)

@router.delete("/{org_id}")
def delete_organization(
    org_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Supprimer une organisation (Administrateur uniquement).
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs.")
        
    return organization_crud.delete_organization(db, org_id)
