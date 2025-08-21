from pydantic import BaseModel
from uuid import UUID

class CategoryBase(BaseModel):
    name: str
    image: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = None
    image: str | None = None

class CategoryOut(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True
