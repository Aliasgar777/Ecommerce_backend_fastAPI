import re
from pydantic import BaseModel, EmailStr, Field, field_validator

class Token(BaseModel):
    access_token: str
    refresh_token : str
    token_type: str


class ResponseUser(BaseModel):
    name : str = Field(...)
    email : EmailStr = Field(...)
    role: str 

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

class SigninRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email:EmailStr

from fastapi import Form
from pydantic import BaseModel, field_validator
import re

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @classmethod
    def as_form(
        cls,
        token: str = Form(...),
        new_password: str = Form(...)
    ):
        return cls(token=token, new_password=new_password)

    @field_validator("new_password")
    @classmethod
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
