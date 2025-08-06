from pydantic import BaseModel
class RestaurantOut(BaseModel):
    res_id:str
    restaurant_name:str
    restaurant_address:str
    restaurant_cuisine:str
    restaurant_rating:float
    class Config:
        orm_mode=True