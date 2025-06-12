from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from .models import Product 

class ProductBase(BaseModel):
    name : str
    description: str
    price : float
    stock: int
    category:str
    image_url: str


class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str]
    image_url: Optional[str]

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

class ProductSearchResponse(BaseModel):
    products : List[ProductResponse]
    message : Optional[str]
