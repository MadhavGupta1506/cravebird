from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.future import select
from fastapi.security import  OAuth2PasswordRequestForm,OAuth2PasswordBearer

from ..models import user as user_table
from .. import utils,oauth2
from ..schemas import auth 
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from uuid import uuid4



router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login",)
async def login(user: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    res=await db.execute(select(user_table.Users).where(user_table.Users.email==user.username))
    res=res.scalar_one_or_none()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User Not Found!")
    check_password=await utils.check_password(user.password,res.password)
    if not check_password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Password or Email!")
    access_token=await oauth2.create_access_token({"id":str(res.id)})
    return {"token":access_token,"token_type":"bearer"}


@router.post("/signup",response_model=auth.UserOut)
async def signup(user: auth.UserCreate, db: AsyncSession = Depends(get_db)):
    res=await db.execute(select(user_table.Users).where(user_table.Users.email==user.email))
    res=res.scalar_one_or_none()
    if res:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already exists! Try login.")
    hashed_password=await utils.hash_password(user.password)
    user.password=hashed_password
    user=user_table.Users(**user.model_dump(),id=str(uuid4()))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user