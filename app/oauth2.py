from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .models import user

from .schemas import schemas
from .config import settings
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import datetime as dt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from . import config, database
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        user_id = payload.get("id")
        print(user_id)
        if user_id is None:
            raise credentials_exception
        return schemas.TokenData(id=user_id)
    except JWTError as e:
        print("JWT Error:", str(e))
        raise credentials_exception

# Function to get the current user based on the token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})
    access_token = verify_access_token(token, credentials_exception)
    curr_user = await db.execute(select(user.Users).filter(user.Users.id == str(access_token.id)))
    curr_user = curr_user.scalars().first()

    return curr_user

# Function to require a specific role for access
def require_role(required_role: list):
    def role_checker(user: user.Users = Depends(get_current_user)):
        if (user.role).lower() not in required_role:
            # print(user.role.lower())
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")
        return user
    
    return role_checker
