import re
from pydantic import BaseModel, EmailStr, Field, field_validator

class Token(BaseModel):
    access_token: str
    refresh_token : str
    token_type: str = "Bearer"

class ResponseUser(BaseModel):
    name : str = Field(..., min_length=3, max_length=10)
    email : EmailStr = Field(...)
    role: str = "user"

class UserInDb(ResponseUser):
    password: str = Field(...)

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        return v
    
    @field_validator("email")
    def validate_email(cls, v):
        domain = v.split('@')[-1]
        if domain not in ['gmail.com', 'nucleusteq.org']:
            raise ValueError("Email must be from 'gmail.com' or 'nucleusteq.org'")
        return v

class SigninRequest(BaseModel):
    email: EmailStr
    password: str
    @field_validator("email")
    def validate_email(cls, v):
        domain = v.split('@')[-1]
        if domain not in ['gmail.com', 'nucleusteq.org']:
            raise ValueError("Email must be from 'gmail.com' or 'nucleusteq.org'")
        return v

class ForgotPasswordRequest(BaseModel):
    email:EmailStr

    @field_validator("email")
    def validate_email(cls, v):
        domain = v.split('@')[-1]
        if domain not in ['gmail.com', 'nucleusteq.org']:
            raise ValueError("Email must be from 'gmail.com' or 'nucleusteq.org'")
        return v

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

class NewTokenRquest(BaseModel):
    refresh_token : str