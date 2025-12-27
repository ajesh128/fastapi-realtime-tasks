from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

Role = Literal["admin","installer"]

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=2)
    role: Role

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int