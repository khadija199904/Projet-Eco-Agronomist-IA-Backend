from src.core.security import password_hash
from src.database.models.users import USER
from src.api.schemas.user_schema import UserCreate

def create_user (db: Session,user : UserCreate):
    hashed_password = password_hash(user.password)
    new_user = USER(email= user.email,username=user.username,password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 





def update_user(db: Session,user_id: int, user_update: UserUpdate):
  
    db_user = db.query(USER).filter(USER.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # exclude_unset=True permet de ne récupérer QUE les champs envoyés par le client
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "password":
            setattr(db_user, "password_hash", password_hash(value))
        else:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user