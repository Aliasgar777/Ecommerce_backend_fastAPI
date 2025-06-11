# app/auth/routes.py
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
def signin(sigin_data: schemas.SigninRequest, db: Session = Depends(get_db)):
    user = utils.authenticate_user(sigin_data.email, sigin_data.password, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token_expires = timedelta(days=float(REFRESH_TOKEN_EXPIRE_DAYS))

    access_token = utils.create_access_token(data={"sub": user.email, "id" : user.id, "role": user.role}, expires_delta=access_token_expires)
    refresh_token = utils.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/auth/signup", response_model=schemas.ResponseUser)
def signup(signup_data :schemas.UserInDb, db: Session = Depends(get_db)):
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


@router.post("/auth/forgot-password")
def forgot_password(request:schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_reset_token(user.email)
    logger.info(token)
    send_reset_email(user.email, token)
    return {"message": "Password reset email sent"}

@router.post("/auth/reset-password")
def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return HTMLResponse(content="<h3>Password updated successfully</h3>")

@router.get("/auth/reset-password-form")
def reset_password_form(token: str):
    html_content = f"""
    <html>
        <body>
            <h2>Reset Your Password</h2>
            <form method="post" action="/auth/reset-password">
                <input type="hidden" name="token" value="{token}">
                <label>New Password:</label><br>
                <input type="password" name="new_password" required><br><br>
                <button type="submit">Reset Password</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)