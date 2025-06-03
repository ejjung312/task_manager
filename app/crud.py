from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

def create_user(db: Session, user: schemas.UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pw = pwd_context.hash(user.password) 

    db_user = models.User(
        user_id=user.user_id,
        password=hashed_pw,
        email=user.email,
        name=user.name
    )
    db.add(db_user) # 현재 세션에 추가. INSERT는 되지 않음
    db.commit() # DB에 영구 반영영
    db.refresh(db_user) # 커밋한 객체의 상태를 DB에서 다시 가져옴(created_at)

    return db_user

def get_user_by_id(db: Session, user_id: str):
    User = models.User

    return db.query(User).filter(User.user_id == user_id).first()