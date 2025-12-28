from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator
import re
from typing import Literal, Optional
from datetime import datetime

Role = Literal["admin","user"]

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character")
    name: str = Field(min_length=2)
    role: Role
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\"\\|,.<>\/?]', v):
            raise ValueError('Password must contain at least one special character')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        return v

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Role
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True