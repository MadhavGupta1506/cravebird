from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from ..oauth2 import get_current_user, require_role

from app.models.category import Category
from app.models import user as user_table
from app.schemas import category as category_schema
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])

# CREATE
@router.post("/", response_model=category_schema.CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: category_schema.CategoryCreate,
    user: user_table.Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    role: str = Depends(require_role(["admin"]))
):
    new_category = Category(id=uuid4(), **category.model_dump())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

# READ (all)
@router.get("/", response_model=list[category_schema.CategoryOut])
async def get_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category))
    return res.scalars().all()

# READ (one)
@router.get("/{category_id}", response_model=category_schema.CategoryOut)
async def get_category(category_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category).where(Category.id == category_id))
    category = res.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

# UPDATE
@router.put("/{category_id}", response_model=category_schema.CategoryOut)
async def update_category(
    category_id: str,
    category: category_schema.CategoryUpdate,
    user: user_table.Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    role: str = Depends(require_role(["admin"]))
):
    res = await db.execute(select(Category).where(Category.id == category_id))
    db_category = res.scalar_one_or_none()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in category.model_dump(exclude_unset=True).items():
        setattr(db_category, field, value)

    await db.commit()
    await db.refresh(db_category)
    return db_category

# DELETE
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    user: user_table.Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    role: str = Depends(require_role(["admin"]))
):
    res = await db.execute(select(Category).where(Category.id == category_id))
    category = res.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.delete(category)
    await db.commit()
    return None