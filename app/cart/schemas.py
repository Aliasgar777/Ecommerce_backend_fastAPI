from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

class CartRequest(BaseModel):
    product_id : int = Field(...)
    quantity : PositiveInt = Field(...)

class CartUpdate(BaseModel):
    quantity : PositiveInt = Field(...)

class CartResponse(CartRequest):
    cart_id: int
    user_id : int

    class Config:
        from_attributes = True