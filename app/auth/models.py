from app.core.database import Base
from sqlalchemy import Column, Integer, String , Enum
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)