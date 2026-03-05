from pydantic import EmailStr, BaseModel
from typing import Optional



class UserBase(BaseModel):
    email: EmailStr
    username: str
    

class UserCreate(UserBase):
    password: str
    


class UserOut(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    message: str
    user: UserOut