from passlib.context import CryptContext
from .config import SECRET_KEY
from jose import jwt


pwd = CryptContext(schemes=["argon2"],deprecated="auto")

def password_hash(password):
    return pwd.hash(password)


def verify_password_hash(password: str, hashed_password: str):
    return pwd.verify(password,hashed_password)




def create_access_token(user):
    payload = { 
        "id": user.id,
        "sub": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else user.role,
        "organization_id": user.organization_id
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None