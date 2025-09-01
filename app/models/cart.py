from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Cart(Base):
    __tablename__="cart"
    cart_id=Column(UUID(as_uuid=True),nullable=False,primary_key=True)
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),unique=True,nullable=False)
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
class CartItem(Base):
    __tablename__="cart_item"
    id=Column(UUID(as_uuid=True),nullable=False,primary_key=True)
    product_id=Column(UUID(as_uuid=True),ForeignKey("products.id", ondelete="CASCADE"),nullable=False)
    quantity=Column(Integer,nullable=False)
    price=Column(Integer,nullable=False)
    cart_id=Column(UUID(as_uuid=True),ForeignKey("cart.cart_id", ondelete="CASCADE"),nullable=False)
    cart = relationship("Cart", back_populates="items")