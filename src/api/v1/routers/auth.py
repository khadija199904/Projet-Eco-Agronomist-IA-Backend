from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from src.api.schemas.user_schema import UserCreate 
from src.database.models.users import USER
from src.api.crud.user_crud import create_user
from src.core.security import verify_password_hash ,create_token
from src.api.dependencies import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter( prefix="/auth", tags=["Authentification"])

@router.post('/register')
async def Register(user : UserCreate ,db: Session = Depends(get_db)) :

   if not user.username.strip() or not user.password.strip() or not user.email.strip() :
    
    raise HTTPException(
        status_code=400,
        detail="Veuillez remplir tous les champs : nom d'utilisateur et mot de passe."
    )
   
   
   existing_user = db.query(USER).filter(USER.email == user.email, USER.username == user.username).first() 
   if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")
   
   new_user = create_user(user)
   print("Nouvel utilisateur créé :", new_user)
   print(new_user)
   db.add(new_user)
   db.commit()
   db.refresh(new_user)
   
   return {"message": "Compte créé avec succès", "username": new_user.username}




@router.post("/login") 
async def login(user : OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
     print(f"Tentative de connexion pour : {user.username}")
     if not user.username.strip() or not user.password.strip():
        raise HTTPException(status_code=400, detail="Email et password requis")
     
     user_data = db.query(USER).filter(
         (USER.email == user.username) | (USER.username == user.username)
     ).first()
     
     if not user_data or not verify_password_hash(user.password,user_data.password_hash):
        raise HTTPException(status_code=401,detail="Access Failed (Incorrect Identifiant or password)")
        
     
     token = create_token(user_data) 
     return {    
             "access_token": token,
             "token_type": "bearer"
               }