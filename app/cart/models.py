from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Relationship
class Cart(Base):
    __tablename__ = "cart"

    cart_id=Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer ,ForeignKey("users.id") ,nullable=False)
    product_id = Column(Integer,ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    user = Relationship("Users", back_populates="cart")
    product = Relationship("Product", back_populates="in_cart")