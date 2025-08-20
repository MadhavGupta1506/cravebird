import uuid
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__="products"
   
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    image = Column(String(255), nullable=True)

    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    category = relationship("Category", back_populates="products", lazy="joined")
    vendor = relationship("Users", back_populates="products", lazy="joined")
