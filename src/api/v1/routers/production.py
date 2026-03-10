from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.lot_schema import LotRecolteCreate, LotRecolteResponse
from src.api.v1.crud import lot_crud
from src.database.models.users import User
from src.database.models.enums import UserRole

router = APIRouter()

@router.post("/", response_model=LotRecolteResponse)
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
