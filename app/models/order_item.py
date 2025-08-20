import uuid
from sqlalchemy import Column, ForeignKey, Integer, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)  # Unit price at time of order

    order = relationship("Order", back_populates="items", lazy="joined")
    product = relationship("Product", lazy="joined")
