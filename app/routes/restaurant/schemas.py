from pydantic import BaseModel
class RestaurantOut(BaseModel):
    res_id:str
    restaurant_name:str
    restaurant_address:str
    restaurant_cuisine:str
    restaurant_rating:float
    class Config:
        orm_mode=True

class menuOut(BaseModel):
    res_id:str
    restaurant:str
    category:str
    item_name:str
    price:float
    class Config:
        orm_mode=True
class menuCreate(BaseModel):
    res_id:str
    category:str
    item_name:str
    price:float
class menuOut(BaseModel):
    res_id:str
    restaurant:str
    category:str
    item_name:str
    price:float
    class Config:
        orm_mode=True   