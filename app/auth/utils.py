# app/auth/utils.py
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import load_dotenv
import os , jwt

from app.auth import models, schemas
from app.core.database import get_db

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str, db: Session):
    stmt = select(models.Users).where(models.Users.email == email)
    result = db.execute(stmt).scalar_one_or_none()
    return result


def authenticate_user(email: str,password: str,db:Session):
    user = get_user(email, db)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    data_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta 
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, JWT_SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta):

    data_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, JWT_SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt

