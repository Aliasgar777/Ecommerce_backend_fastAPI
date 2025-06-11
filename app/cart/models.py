from app.core.database import Base
from sqlalchemy import Column, Integer

class Cart(Base):
    __tablename__ = "cart"

    cart_id=Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)