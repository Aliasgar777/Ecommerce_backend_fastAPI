# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
import jwt
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.auth import models, schemas, utils
from dotenv import load_dotenv
from app.core.logger import logger
from app.auth.utils import generate_reset_token, verify_reset_token, get_password_hash
from app.auth.service import send_reset_email
import os

router = APIRouter()

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


@router.post("/auth/signin", response_model=schemas.Token)
def signin(
    sigin_data: schemas.SigninRequest,
    db: Session = Depends(get_db)
    ):
    
    logger.info(f"Sign-in attempt for email: {sigin_data.email}")
    user = utils.authenticate_user(sigin_data.email, sigin_data.password, db)
    
    if not user:
        logger.warning(f"Failed login attempt for email: {sigin_data.email}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token_expires = timedelta(days=float(REFRESH_TOKEN_EXPIRE_DAYS))

    access_token = utils.create_access_token(
        data={"sub": user.email, "id" : user.id, "role": user.role},
        expires_delta=access_token_expires
        )
    refresh_token = utils.create_refresh_token(
        data={"sub": user.email, "id" : user.id, "role": user.role},
        expires_delta=refresh_token_expires
        )

    logger.info(f"Successful login for user_id: {user.id}, email: {user.email}")
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}
    

@router.post("/auth/signup", response_model=schemas.ResponseUser)
def signup(
    signup_data :schemas.UserInDb, 
    db: Session = Depends(get_db)
    ):

    logger.info(f"Sign-up attempt for email - {signup_data.email}")
    user = utils.get_user(signup_data.email, db)

    if user:
        logger.warning(f"Sign-up error, email - {signup_data.email} already registered ")
        raise HTTPException(
            status_code=400,
            detail="User already registered")
    
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
        role = user_obj.role 
    )
    logger.info(f"Sign-up succesfull for email - {signup_data.email}")
    return user_reponse


@router.post("/auth/forgot-password")
def forgot_password(
    request:schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db)
    ):
    logger.info("forgot password using free email service")
    user = db.query(models.Users).filter(models.Users.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=f"User with email-{request.email} not found")

    # Generating a url safe token
    token = generate_reset_token(user.email)
    logger.info(f"Reset token for user {request.email} - {token}")

    # Sending a link which contains the reset token
    send_reset_email(user.email, token)
    return {"message": "Password reset email sent"}


@router.post("/auth/reset-password")
def reset_password(
    data : schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
    ):

    token = data.token
    new_password = data.new_password
    logger.info("updating the new password")
    # Get email from token and also verify token
    email = verify_reset_token(token)

    user = utils.get_user(email, db)
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=f"User not found with email - {email}")

    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    logger.info(f"new password updated for user {user.name}")
    return f"password reset complete for user ({user.name}) now login with the new password"


@router.get("/auth/renew-token", response_model=schemas.Token)
def renew_access_token(
    token: schemas.NewTokenRquest, 
    db: Session = Depends(get_db)
    ):
    try:
        payload = jwt.decode(token.refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user = utils.get_user(payload.get("sub"), db)

        if user is None:
            HTTPException(
                status_code=404, 
                detail=f"user with email - {user.email} does not exists")
        
        new_access_token = utils.create_access_token(
            payload, timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)))

        return {
            "access_token" : f"{new_access_token}",
            "refresh_token" :f"{token.refresh_token}",
            "token_type" : "Bearer"
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")