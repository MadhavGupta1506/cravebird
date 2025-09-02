from pydantic import BaseModel
from uuid import UUID

class AddToCart(BaseModel):
    product_id: UUID
    quantity: int

class CartItem(BaseModel):
    product_id: UUID
    name: str
    price: float
    quantity: int
    total_item_price: float

class Cart(BaseModel):
    user_id: UUID
    items: list[CartItem]
    total_price: float
