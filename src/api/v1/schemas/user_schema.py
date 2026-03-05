from pydantic import BaseModel 




class UserBase(BaseModel):
    email: str
    password :str
    

class UserCreate(UserBase):
    username : str
    


class UserOut(UserBase):
    id: int
    is_active: bool
    

    class Config:
        from_attributes = True