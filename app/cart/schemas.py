from pydantic import BaseModel, Field


class CartRequest(BaseModel):
    product_id : int = Field(...)
    quantity : int = Field(...)

class CartUpdate(BaseModel):
    quantity : int = Field(...)

class CartResponse(CartRequest):
    cart_id: int
    user_id : int = Field(...)

    class Config:
        from_attributes = True