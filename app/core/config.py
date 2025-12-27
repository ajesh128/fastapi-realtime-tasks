from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    MONGO_URI: str
    JWT_SECRET_KEY: str = "wK0Gk6cfvCDVeMn9me09zihZZKVpDu"
    JWT_ALGORITHM: str = "HS256"
    FERNET_KEY: str
    CONTROLLER_URL: str
    BALENA_JWT_SECRET_KEY: str
    INTEGRATION_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 10
    REFRESH_TOKEN_EXPIRE_DAYS:int = 7
    GIT_LAB:str
    PROJECT_PATH:str
    TOKEN:str

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings():
    return Settings()


Config = get_settings()
