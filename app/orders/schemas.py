from pydantic import BaseModel
from typing import List
from enum import Enum
from datetime import datetime


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True


class OrderHistoryItem(BaseModel):
    order_id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True
