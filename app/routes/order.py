from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from ..oauth2 import get_current_user, require_role
from app.models.order import Order as OrderModel, OrderItem
from app.models import user as user_table
from app.models.user import UserRole
from app.schemas import order as order_schema
from app.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.routes.notifications import manager as notif_manager

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=order_schema.OrderOut, status_code=status.HTTP_201_CREATED)
async def place_order(db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    # Get user's cart
    cart_res = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = cart_res.scalar_one_or_none()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    cart_items_res = await db.execute(select(CartItem).where(CartItem.cart_id == cart.cart_id))
    cart_items = cart_items_res.scalars().all()
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    total_price = 0
    order_items: list[OrderItem] = []
    touched_vendor_ids: set[str] = set()

    for item in cart_items:
        product_res = await db.execute(select(Product).where(Product.id == item.product_id))
        product = product_res.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stock for {product.name}")

        subtotal = float(product.price) * int(item.quantity)
        total_price += subtotal

        # adjust inventory
        product.stock = int(product.stock) - int(item.quantity)

    order_items.append(
            OrderItem(product_id=item.product_id, quantity=item.quantity, price=product.price, subtotal=subtotal)
        )
    touched_vendor_ids.add(str(product.vendor_id))

    new_order = OrderModel(user_id=current_user.id, total_price=total_price, status="pending", items=order_items)
    db.add(new_order)

    # clear cart
    await db.execute(CartItem.__table__.delete().where(CartItem.cart_id == cart.cart_id))

    await db.commit()
    await db.refresh(new_order)
    # Notify vendors whose products are in the order
    vendor_ids = touched_vendor_ids
    await notif_manager.broadcast_to_vendors(
        vendor_ids,
        {
            "type": "order_created",
            "order_id": str(new_order.id),
            "user_id": str(new_order.user_id),
            "status": new_order.status,
            "total_price": float(new_order.total_price),
        },
    )
    return new_order


@router.get("/me", response_model=list[order_schema.OrderOut])
async def my_orders(db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user)):
    res = await db.execute(select(OrderModel).where(OrderModel.user_id == current_user.id))
    return res.scalars().unique().all()


@router.get("/vendor/incoming", response_model=list[order_schema.VendorOrderOut])
async def vendor_incoming_orders(
    db: AsyncSession = Depends(get_db),
    current_user: user_table.Users = Depends(get_current_user),
    role: str = Depends(require_role(["vendor", "admin"]))
):
    # Fetch orders that contain items belonging to this vendor
    res = await db.execute(select(OrderModel))
    orders = res.scalars().unique().all()

    vendor_orders: list[order_schema.VendorOrderOut] = []
    for order in orders:
        vo_items: list[order_schema.VendorOrderItemOut] = []
        vendor_subtotal = 0.0
        for it in order.items:
            if it.product and it.product.vendor_id == current_user.id:
                name = it.product.name if hasattr(it.product, "name") else "Product"
                vo_items.append(
                    order_schema.VendorOrderItemOut(
                        product_id=str(it.product_id),
                        name=name,
                        quantity=int(it.quantity),
                        price=float(it.price),
                        subtotal=float(it.subtotal),
                    )
                )
                vendor_subtotal += float(it.subtotal)
        if vo_items:
            vendor_orders.append(
                order_schema.VendorOrderOut(
                    order_id=str(order.id),
                    user_id=str(order.user_id),
                    status=order.status,
                    vendor_subtotal=vendor_subtotal,
                    items=vo_items,
                )
            )
    return vendor_orders


@router.patch("/{order_id}/status", status_code=200)
async def update_order_status(order_id: str, payload: order_schema.OrderUpdate, db: AsyncSession = Depends(get_db), current_user: user_table.Users = Depends(get_current_user), role: str = Depends(require_role(["vendor", "admin"]))):
    # Vendors can update status for orders that include their products
    res = await db.execute(select(OrderModel).where(OrderModel.id == order_id))
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # simple guard: ensure at least one item belongs to vendor
    owns_any = any(it.product and it.product.vendor_id == current_user.id for it in order.items)
    if not owns_any and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized for this order")

    order.status = payload.status
    await db.commit()
    await db.refresh(order)
    return {"status": order.status}