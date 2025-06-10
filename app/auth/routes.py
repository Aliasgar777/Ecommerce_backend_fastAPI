# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.auth import models, schemas, utils
from dotenv import load_dotenv
from app.core.logger import logger
import os

router = APIRouter()

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


@router.post("/auth/signin", response_model=schemas.Token)
async def signin(sigin_data: schemas.SigninRequest, db: Session = Depends(get_db)):
    user = utils.authenticate_user(sigin_data.email, sigin_data.password, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token_expires = timedelta(days=float(REFRESH_TOKEN_EXPIRE_DAYS))

    access_token = utils.create_access_token(data={"sub": user.email, "id" : user.id, "role": user.role}, expires_delta=access_token_expires)
    refresh_token = utils.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/auth/signup", response_model=schemas.ResponseUser)
async def signup(signup_data :schemas.UserInDb, db: Session = Depends(get_db)):
    user = utils.get_user(signup_data.email, db)
    logger.info("inside signup")

    if user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    hashed_password = utils.get_password_hash(signup_data.password)

    user_obj = models.Users(
        name = signup_data.name,
        email=signup_data.email,
        hashed_password=hashed_password,
        role=signup_data.role,
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    user_reponse = schemas.ResponseUser(
        name = user_obj.name,
        email = user_obj.email,
        role = user_obj.role or "user"
    )
    return user_reponse

