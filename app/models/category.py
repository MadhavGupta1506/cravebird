import uuid
from sqlalchemy import Column, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    image = Column(String(255), nullable=True)

    products = relationship("Product", back_populates="category", lazy="selectin")
