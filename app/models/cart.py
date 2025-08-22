import uuid
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Cart(Base):
    __table_name__="Cart"
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quantity=Column(Integer, nullable=False)
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)
    product_id=Column(UUID(as_uuid=True),ForeignKey("products.id", ondelete="CASCADE"),nullable=False)
    
    user=relationship("User",lazy="joined")
    product=relationship("Product",lazy="joined")
    
    