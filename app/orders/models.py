from app.core.database import Base
from sqlalchemy import Column, String, Integer, Float

class Orders(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Float)

