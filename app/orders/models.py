import enum
from app.core.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class Orders(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="orders")