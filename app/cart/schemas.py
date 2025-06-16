from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

class CartRequest(BaseModel):
    product_id : int = Field(..., ge=1)
    quantity : int = Field(..., ge=1)

class CartUpdate(BaseModel):
    quantity : int = Field(..., ge=1)

class CartResponse(CartRequest):
    cart_id: int
    user_id : int

    class Config:
        from_attributes = True