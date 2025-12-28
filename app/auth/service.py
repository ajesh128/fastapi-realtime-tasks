import uuid

from fastapi import HTTPException,status
from app.core.config import Config
from app.database.asyncdb.models import Users
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
from jose import jwt
from bson import ObjectId


class AuthService(object):

    @staticmethod
    async def user_validator(email):
        user_exist = await Users().find_one(query={"email": email},projection={"_id":1,"email":1,"role":1,"password":1})
        return user_exist
    
    @staticmethod
    async def get_user_by_id(user_id: str):
        user = await Users().find_one(query={"_id": ObjectId(user_id)}, projection={"password": 0})
        return user
    
    @staticmethod
    async def user_insertion(docs):
        await Users().insert_one(data=docs)
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Treat any hash/verification error as invalid credentials
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def create_token(subject: str, email: str, role: str, expires_delta: timedelta, token_type: str) -> dict:
        now = AuthService._utcnow()
        expire = now + expires_delta
        jti = str(uuid.uuid4())
        payload = {
            "sub": subject,
            "email": email,
            "role": role,
            "type": token_type,
            "jti": jti,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
        return {"token": token, "jti": jti, "exp": expire}
    @staticmethod
    def create_access_token(subject: str, email: str, role: str) -> dict:
        return AuthService.create_token(subject, email, role, timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES), "access")
    
    @staticmethod
    def create_refresh_token(subject: str, email: str, role: str) -> dict:
        return AuthService.create_token(subject, email, role, timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")