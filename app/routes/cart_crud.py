from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID, uuid4
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

@router.delete("/remove_one/{item_id}")
async def remove_one(item_id: UUID, db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    q = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = q.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    q = await db.execute(select(CartItem).where((CartItem.cart_id == cart.cart_id) & ((CartItem.product_id) == item_id)))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    if item.quantity > 1:
        item.quantity -= 1
        item.price = item.quantity * (item.price // item.quantity)  # recalc based on unit price
        await db.commit()
        await db.refresh(item)
        return {"message": "One quantity removed from cart"}
    else:
        await db.delete(item)
        await db.commit()
        return {"message": "Item removed from cart"}

@router.delete("/clear_cart")
async def clear_cart(db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    q=await db.execute(select(Cart).where(Cart.user_id==current_user.id))
    cart=q.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    q=await db.execute(select(CartItem).where(CartItem.cart_id==cart.cart_id))
    items=q.scalars().all()
    for item in items:
        await db.delete(item)
    await db.commit()
    return  {"message":"Cart cleared"} 
@router.get("/total_price")
async def total_price(db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    q=await db.execute(select(Cart).where(Cart.user_id==current_user.id))
    cart=q.scalar_one_or_none() 
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    q=await db.execute(select(CartItem).where(CartItem.cart_id==cart.cart_id))
    items=q.scalars().all()
    total_price=0
    for item in items:
        total_price+=item.price
    return {"total_price":total_price}
@router.get("/cart_details",response_model=cart_schema.Cart)
async def cart_details(db: AsyncSession = Depends(get_db), current_user: user_table.Users= Depends(get_current_user)):
    q=await db.execute(select(Cart).where(Cart.user_id==current_user.id))
    cart=q.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    q=await db.execute(select(CartItem).where(CartItem.cart_id==cart.cart_id))
    items=q.scalars().all()
    cart_items=[]
    total_price=0
    for item in items:
        q=await db.execute(select(Product).where(Product.id==item.product_id))
        product=q.scalar_one_or_none()
        if product:
            total_item_price=item.price
            cart_item=cart_schema.CartItem(
                product_id=item.product_id,
                name=product.name,
                price=product.price,
                quantity=item.quantity,
                total_item_price=total_item_price
            )
            cart_items.append(cart_item)
            total_price+=total_item_price
    return cart_schema.Cart(
        user_id=current_user.id,
        items=cart_items,
        total_price=total_price
    )
