from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

# 함수의 결과값을 메모리에 저장해 저장된 값을 반환
@lru_cache()
def get_settings():
    return Settings()