from pydantic import BaseModel
class UserCreate(BaseModel):
    email: str
    firstname: str
    lastname: str
    password: str
    phone_number: str

class UserOut(BaseModel):
    user_id: str
    email: str
    firstname: str
    lastname: str
    phone_number: str


class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    id:str