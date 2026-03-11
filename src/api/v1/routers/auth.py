from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.schemas.user_schema import UserCreate, UserResponse, UserUpdate, UserOut, Token
from src.database.models import User
from src.api.v1.crud.user_crud import create_user, update_user
from src.core.security import verify_password_hash, create_access_token
from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from src.database.models.organization_table import Organization

router = APIRouter()

@router.post('/register', response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if not user.username.strip() or not user.password.strip() or not user.email.strip():
        raise HTTPException(
            status_code=400,
            detail="Veuillez remplir tous les champs : nom d'utilisateur et mot de passe."
        )
   
    existing_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first() 
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")
   
    new_user = create_user(db, user)
   
    return {
        "message": "Compte créé avec succès",
        "user": new_user
    }

@router.post("/login", response_model=Token) 
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Tentative de connexion pour : {user.username}")
    if not user.username.strip() or not user.password.strip():
        raise HTTPException(status_code=400, detail="Email et password requis")
     
    user_data = db.query(User).filter(
        (User.email == user.username) | (User.username == user.username)
    ).first()
     
    if not user_data or not verify_password_hash(user.password, user_data.hashed_password):
        raise HTTPException(status_code=401, detail="Access Failed (Incorrect Identifiant or password)")
        
    token = create_access_token(user_data) 
    return {    
        "access_token": token,
        "token_type": "bearer"
    }

@router.patch("/users/me", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    updated_user = update_user(db, current_user.id, user_data)
    
    return {
        "message": "Profil mis à jour avec succès",
        "user": updated_user
    }