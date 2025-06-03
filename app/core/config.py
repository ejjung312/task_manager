from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    EMAIL_SECRET_KEY: str

    class Config:
        env_file = ".env"

# 함수의 결과값을 메모리에 저장해 저장된 값을 반환
@lru_cache()
def get_settings():
    return Settings()