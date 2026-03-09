from sqlalchemy.orm import Session
from src.core.security import password_hash
from src.database.models.users import User
from src.api.v1.schemas.user_schema import UserCreate, UserUpdate
from fastapi import HTTPException

def create_user(db: Session, user: UserCreate):
    hashed_password = password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        full_name=user.full_name,
        phone=user.phone,
        profile_image_url=user.profile_image_url,
        organization_id=user.organization_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "password":
            setattr(db_user, "hashed_password", password_hash(value))
        else:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user