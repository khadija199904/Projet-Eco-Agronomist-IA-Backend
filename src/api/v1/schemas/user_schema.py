from pydantic import EmailStr, BaseModel, ConfigDict
from typing import Optional
from src.database.models.enums import UserRole

class UserBase(BaseModel):
    email: str
    username: str
    role: UserRole
    full_name: Optional[str] = None
    organization_id: Optional[int] = None


class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    full_name: Optional[str] = None
    organization_id: Optional[int] = None
    

class UserResponse(BaseModel):
    message: str
    user: UserOut

class Token(BaseModel):
    access_token: str
    token_type: str