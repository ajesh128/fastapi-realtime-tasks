from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    MONGO_URI: str
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings():
    return Settings()


Config = get_settings()
