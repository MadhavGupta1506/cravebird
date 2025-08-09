from pydantic import BaseModel

class AddressCreate(BaseModel):
    address_line1: str
    address_line2: str
    city: str
    state: str
    zip_code: int
    country: str
class AddressOut(BaseModel):
    id: int
    address_line1: str
    address_line1: str
    city: str
    state: str
    zip_code: int
    country: str
    class Config:
        from_attributes = True