from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..oauth2 import get_current_user
from app.models.product import Product as product_table
from app.models.user import Users as user_table
from app.schemas import product
from app.database import get_db
router = APIRouter(tags=["Search Products"])

@router.get("/search", response_model=list[product.SearchProductOut])
async def search_products(
    query: product.SearchProduct,
    db: AsyncSession = Depends(get_db),
    user: user_table = Depends(get_current_user)
):
    res = await db.execute(
        select(product_table).where(product_table.name.ilike(f"%{query.query}%"))
    )
    products = res.scalars().all()
    
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    
    # Map products to include vendor_name
    result = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "category_id": p.category_id,
            "image": p.image,
            "vendor_name": f"{p.vendor.firstname} {p.vendor.lastname}"
        }
        for p in products
    ]
    return result
