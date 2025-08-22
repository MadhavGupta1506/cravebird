from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from ..oauth2 import get_current_user, require_role

from app.models.category import Category
from app.models import user as user_table
from app.schemas import category as category_schema
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])
@router.get("/")
async def get_cart(user: user_table.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q=await db.execute(select(user_table.User).where(user_table.User.id==user.id))
    q=q.scalars().all()
    return q.scalars().first()
