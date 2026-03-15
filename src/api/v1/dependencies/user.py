from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.config import SECRET_KEY 
from src.database.models.users import User
from jose import JWTError, jwt
from src.api.v1.dependencies.db import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    
    try:
       payload = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
       user_id = payload.get("id")
       if user_id is None:
           raise HTTPException(status_code=403, detail="Token invalide : ID utilisateur absent")
       
    except JWTError:
      raise HTTPException(status_code=401, detail="Token expiré ou corrompu")

    user_db = db.query(User).filter(User.id == user_id).first()
    
    if not user_db:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user_db