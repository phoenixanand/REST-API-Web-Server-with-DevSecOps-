from pydantic import BaseModel, EmailStr
from typing import Optional

class UserOut(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        orm_mode = True

class Post(BaseModel):
    first_name : str
    last_name : str
    age : int
    published : bool = True
    owner_id: int
    owner: UserOut


class PostBase(BaseModel):
    first_name : str
    last_name : str
    age : int
    published : bool = True
    phone_number :Optional[int] = None


class PostCreate(PostBase):
    pass
    
class PostUpdate(PostBase):
    pass   

class PostResponse(BaseModel):
    id: int
    first_name : str
    last_name : str
    age : int
    published: bool
    phone_number :Optional[int] = None

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr 
    password: str



class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):    ## to print to the user about the token and type
    access_token: str
    token_type: str

class TokenData(BaseModel): # input to the data in the oauth
    id: Optional[int] = None

