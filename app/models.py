from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey,TIMESTAMP,Boolean, FLOAT
from sqlalchemy.sql import text

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    user_id = Column(String,  nullable=False)
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