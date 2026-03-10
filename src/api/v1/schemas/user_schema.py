from pydantic import EmailStr, BaseModel, field_validator
from typing import Optional
from src.database.models.enums import UserRole

class UserBase(BaseModel):
    email: str
    username: str
    role: UserRole
    full_name: Optional[str] = None
    organization_id: Optional[int] = None

    @field_validator("organization_id", mode="before")
    @classmethod
    def clean_id(cls, v):
        if v == 0 or v == "0":
            return None
        return v

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

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