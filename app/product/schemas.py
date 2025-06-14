from typing import Optional, List
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from .models import Product 

class ProductBase(BaseModel):
    name : str = Field(..., min_length=3, max_length=10)
    description: str = Field(...)
    price : PositiveFloat = Field(...)
    stock : PositiveInt = Field(...)
    category: str = Field(...)
    image_url: str = Field(...)


class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None,min_length=3, max_length=10)
    description: Optional[str]
    price: Optional[PositiveFloat] 
    stock: Optional[PositiveInt]
    category: Optional[str]
    image_url: Optional[str]

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

class ProductSearchResponse(BaseModel):
    products : List[ProductResponse]
    message : Optional[str]
