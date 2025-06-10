from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String , Float, URL
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # SQLAlchemy relationship (backref optional)
    creator = relationship("Users", back_populates="products")
