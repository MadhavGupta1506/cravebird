import enum
import uuid
from sqlalchemy import Column, Enum, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    total_price = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("Users", back_populates="orders", lazy="joined")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")
