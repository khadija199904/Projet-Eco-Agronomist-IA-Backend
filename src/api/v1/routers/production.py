from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.lot_schema import LotRecolteCreate, LotRecolteResponse, LotRecolteUpdate
from src.api.v1.crud import lot_crud
from src.database.models.users import User
from src.database.models.enums import UserRole

router = APIRouter()

@router.post("/lot_recolte", response_model=LotRecolteResponse)
def creer_lot(
    lot_data: LotRecolteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user) 
):
    
    if user.role != UserRole.AGRICULTEUR:
        raise HTTPException(status_code=403, detail="Réservé aux agriculteurs.")
    
    if user.organization_id != lot_data.ferme_id:
        raise HTTPException(status_code=403, detail="Vous n'appartenez pas à cette ferme.")

    return lot_crud.create_lot(db=db, lot=lot_data, agriculteur_id=user.id)


@router.get("/ma-ferme", response_model=List[LotRecolteResponse])
def lister_mes_lots(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.organization_id:
        raise HTTPException(status_code=400, detail="Vous n'êtes assigné à aucune ferme.")
        
    return lot_crud.get_lots_by_ferme(db=db, ferme_id=user.organization_id)

@router.get("/lots", response_model=List[LotRecolteResponse])
def lister_tous_les_lots(
    ferme_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Lister tous les lots (réservé aux STATIONS et ADMINS).
    Permet de filtrer par ferme pour la réception.
    """
    if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")
    
    return lot_crud.get_lots(db, ferme_id=ferme_id)

@router.put("/lot_recolte/{lot_id}", response_model=LotRecolteResponse)
def modifier_lot(
    lot_id: int,
    lot_update: LotRecolteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != UserRole.AGRICULTEUR:
        raise HTTPException(status_code=403, detail="Réservé aux agriculteurs.")
        
    db_lot = lot_crud.get_lot_by_id(db, lot_id)
    if not db_lot:
        raise HTTPException(status_code=404, detail="Lot introuvable.")
        
    if db_lot.ferme_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Accès refusé.")
        
    return lot_crud.update_lot(db, lot_id, lot_update)

@router.delete("/lot_recolte/{lot_id}")
def supprimer_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != UserRole.AGRICULTEUR:
        raise HTTPException(status_code=403, detail="Réservé aux agriculteurs.")
        
    db_lot = lot_crud.get_lot_by_id(db, lot_id)
    if not db_lot:
        raise HTTPException(status_code=404, detail="Lot introuvable.")
        
    if db_lot.ferme_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Accès refusé.")
        
    success = lot_crud.delete_lot(db, lot_id)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression.")
        
    return {"message": "Lot supprimé avec succès."}
