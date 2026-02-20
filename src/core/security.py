from passlib.context import CryptContext
from .config import SECRET_KEY
from jose import jwt


pwd = CryptContext(schemes=["argon2"],deprecated="auto")

def password_hash(password):
    return pwd.hash(password)


def verify_password_hash(password: str, hashed_password: str):
    return pwd.verify(password,hashed_password)




def create_access_token(user:dict):
    payload = { "id": user.id}

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token