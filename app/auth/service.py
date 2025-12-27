import uuid
from app.core.config import Config
from app.database.asyncdb.models import Users
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
from jose import jwt


class AuthService(object):

    @staticmethod
    async def user_validator(email):
        user_exist = await Users().find_one(query={"email": email},)
        return user_exist
    @staticmethod
    async def user_insertion(docs):
        await Users().insert_one(data=docs)
    @staticmethod
    def hash_password(password: str) -> str:
        print(password,"password")
        return pwd_context.hash(password)
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
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
        return AuthService.create_token(subject, email, role, timedelta(minutes=10), "access")
    
    @staticmethod
    def create_refresh_token(subject: str, email: str, role: str) -> dict:
        return AuthService.create_token(subject, email, role, timedelta(days=2), "refresh")