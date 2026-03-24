from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.core.security import password_hash
from src.database.models.users import User
from src.api.v1.schemas.user_schema import UserCreate, UserUpdate

def create_user(db: Session, user: UserCreate):
    user_data = user.model_dump(exclude={"password"})
    
    if user_data.get("organization_id") == 0 or user_data.get("organization_id") == "0":
        user_data["organization_id"] = None

    hashed_password = password_hash(user.password)
    
    new_user = User(
        **user_data, 
        hashed_password=hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        db.rollback()

        raise HTTPException(
            status_code=400, 
            detail=f"Erreur d'intégrité : {str(e.orig)}"
        )

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "password":
            setattr(db_user, "hashed_password", password_hash(value))
        elif key == "organization_id" and (value == 0 or value == "0"):
            setattr(db_user, "organization_id", None)
        else:
            setattr(db_user, key, value)
            
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mise à jour impossible : conflit de données (email/username)")