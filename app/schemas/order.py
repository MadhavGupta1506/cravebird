from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float
    subtotal: float

class OrderCreate(BaseModel):
    items: List[OrderItem]
    total_price: float
    status: Optional[str] = Field(default="pending")
    user_id: str
    
class OrderOut(BaseModel):
    id: str
    user_id: str
    status: str
    total_price: float
    items: List[OrderItem]

    class Config:
        orm_mode = True

class OrderUpdate(BaseModel):
    status: str
    total_price: Optional[float] = None
    items: Optional[List[OrderItem]] = None
class OrderList(BaseModel):
    orders: List[OrderOut]
    class Config:
        orm_mode = True
        
class PlaceOrder(BaseModel):
    cart_id: str


# Vendor-facing responses
class VendorOrderItemOut(BaseModel):
    product_id: str
    name: str
    quantity: int
    price: float
    subtotal: float

class VendorOrderOut(BaseModel):
    order_id: str
    user_id: str
    status: str
    vendor_subtotal: float
    items: List[VendorOrderItemOut]
