from ..database import Base
from sqlalchemy import Column, Integer, String, ForeignKey,TIMESTAMP,Boolean, FLOAT
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
import enum
from sqlalchemy import Column, String, Enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VENDOR = "vendor"
    DELIVERY_PARTNER = "delivery_partner"
    CUSTOMER = "customer"
    
class Users(Base):
    __tablename__ = 'users'
    id = Column(UUID,primary_key=True,unique=True, nullable=False)
    email = Column(String, unique=True,index=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone_number=Column(String,nullable=False)
    role=Column(Enum(UserRole),nullable=False,index=True,default="customer")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    products = relationship("Product", back_populates="vendor", lazy="selectin")

