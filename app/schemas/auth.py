from pydantic import BaseModel
from typing import Optional
from uuid import UUID
class UserCreate(BaseModel):
    email:str 
    firstname:str
    lastname:str
    password:str
    phone_number:str
    role:Optional[str]
    
class UserOut(BaseModel):
    id:UUID 
    email:str 
    firstname:str
    lastname:str
    phone_number:str
    role:str