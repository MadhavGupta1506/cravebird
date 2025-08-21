from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from ..oauth2 import get_current_user, require_role

from app.models.product import Product as product_table
from app.models import user as user_table
from app.schemas import product 
from app.database import get_db
router = APIRouter(prefix="/products", tags=["Products"])

# CREATE
@router.post("/", response_model=product.ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product: product.ProductCreate,user:user_table=Depends(get_current_user), db: AsyncSession = Depends(get_db),role:str=Depends(require_role(["admin","vendor"]))):
    new_product = product_table(id=uuid4(), **product.model_dump(),vendor_id=user.id)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

# READ (all) for vendor
@router.get("/", response_model=list[product.ProductOut])
async def get_products_by_vendor(db: AsyncSession = Depends(get_db),user:user_table=Depends(get_current_user),role:str=Depends(require_role(["admin","vendor"]))):
    res = await db.execute(select(product_table).where(product_table.vendor_id==user.id))
    products = res.scalars().all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")
    return products


# READ (all) for customer
@router.get("/all", response_model=list[product.ProductOut])
async def get_products(db: AsyncSession = Depends(get_db), user:user_table=Depends(get_current_user)):
    res = await db.execute(select(product_table))
    products = res.scalars().all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")
    return products

# READ (one) for vendor
@router.get("/{product_id}", response_model=product.ProductOut)
async def get_product_by_vendor(product_id: str,user:user_table=Depends(get_current_user), db: AsyncSession = Depends(get_db),role:str=Depends(require_role(["admin","vendor"]))):
    res = await db.execute(select(product_table).where(product_table.id == product_id and product_table.vendor_id==user.id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product
@router.get("/one/{id}",response_model=product.ProductOut)
async def get_product(id:str,user:user_table=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    res= await db.execute(select(product_table).where(product_table.id==id))
    product=res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# UPDATE
@router.put("/{product_id}", response_model=product.ProductOut)
async def update_product(product_id: str, product: product.ProductUpdate,user:user_table=Depends(get_current_user), db: AsyncSession = Depends(get_db),role:str=Depends(require_role(["admin","vendor"]))):
    res = await db.execute(select(product_table).where(product_table.id == product_id))
    db_product = res.scalar_one_or_none()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.vendor_id!=user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    for field, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)

    await db.commit()
    await db.refresh(db_product)
    return db_product

# DELETE
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, user:user_table=Depends(get_current_user), db: AsyncSession = Depends(get_db),role:str=Depends(require_role(["admin","vendor"]))):
    res = await db.execute(select(product_table).where(product_table.id == product_id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.vendor_id!=user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    await db.delete(product)
    await db.commit()
    return None
