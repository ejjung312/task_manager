from pydantic import BaseModel, Field
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str | None = None

class UserLogin(BaseModel):
    user_id: str
    password: str

class UserCreate(BaseModel):
    user_id: str = Field(..., max_length=30) # Pydantic에서 필수값 의미
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6)
    name: str = Field(..., max_length=50)

class UserOut(BaseModel):
    user_id: str
    name: str
    created_at: datetime

    """
    ORM -> DTO 변환
    """
    class Config:
        from_attributes = True