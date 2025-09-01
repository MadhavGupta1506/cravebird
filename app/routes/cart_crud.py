from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from ..oauth2 import get_current_user, require_role


from app.models import user as user_table
from app.models.cart import Cart,CartItem
from app.models.product import Product 
from app.schemas import cart as cart_schema
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add_to_cart")
async def add_to_cart(items:cart_schema.AddToCart,db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    product_id,quantity=items.product_id,items.quantity
    q=await db.execute(select(Cart).where(Cart.user_id==current_user.id))
    cart=q.scalar_one_or_none()
    if not cart:
        cart=Cart(cart_id=str(uuid4()),user_id=current_user.id)
        db.add(cart)
        await db.commit()
        db.refresh(cart)
    q=await db.execute(select(Product).where(product_id==Product.id))
    product=q.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    q=await db.execute(select(CartItem).where((CartItem.cart_id==cart.cart_id )& (CartItem.product_id==product.id)))
    item=q.scalar_one_or_none()
    if item:
        item.quantity+=quantity
        item.price=product.price*item.quantity
        await db.commit()
        await db.refresh(item)
    else:
        item=CartItem(id=(uuid4()),cart_id=cart.cart_id,product_id=product.id,quantity=quantity,price=product.price)
        db.add(item)
        await db.commit()
        await db.refresh(item)
    return {"message":"Item added to cart"}


@router.get("/get_cart")
async def get_cart(db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    q=await db.execute(select(Cart).where(Cart.user_id==current_user.id))
    cart=q.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    q=await db.execute(select(CartItem).where(CartItem.cart_id==cart.cart_id))
    items=q.scalars().all()
    return items