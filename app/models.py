from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey,TIMESTAMP,Boolean, FLOAT
from sqlalchemy.sql import text

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    user_id = Column(String,unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone_number=Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

class Restaurants(Base):
    __tablename__ = 'restaurants'
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    res_id=Column(String,nullable=False)
    restaurant_name=Column(String,nullable=False)
    restaurant_address=Column(String,nullable=False)
    restaurant_cuisine=Column(String,nullable=False)
    restaurant_rating=Column(FLOAT,nullable=False)
    
class Menu(Base):
    __tablename__ = 'menu'
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    res_id=Column(String,nullable=False)
    restaurant=Column(String,nullable=False)
    category=Column(String,nullable=False)
    item_name=Column(String,nullable=False)
    price=Column(FLOAT,nullable=False)

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(Integer, nullable=False)
    country = Column(String, nullable=False)