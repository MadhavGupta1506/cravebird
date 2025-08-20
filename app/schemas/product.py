from pydantic import BaseModel
from uuid import UUID

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    image:str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None

class ProductOut(ProductBase):
    id: UUID

    class Config:
        from_attributes = True   # Needed for SQLAlchemy → Pydantic
