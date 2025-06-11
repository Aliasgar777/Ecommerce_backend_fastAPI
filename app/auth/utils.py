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
from itsdangerous import URLSafeTimedSerializer,BadSignature, SignatureExpired
from app.core.logger import logger

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
RESET_TOKEN_SECRET = os.getenv("RESET_TOKEN_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin")

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


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        id = payload.get("id")
        if email is None or id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

serializer = URLSafeTimedSerializer(secret_key=RESET_TOKEN_SECRET) 

def generate_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="reset-password")

def verify_reset_token(token: str, max_age: int = 3600) -> str | None:
    try:
        return serializer.loads(token, salt="reset-password", max_age=max_age)
    except SignatureExpired:
        logger.error("Token expired.")
    except BadSignature:
        logger.error("Invalid token.")
    return None