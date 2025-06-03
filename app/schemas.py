from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str = Field(..., max_length=30) # Pydantic에서 필수값 의미
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