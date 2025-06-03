from sqlalchemy.orm import Session
from . import models, schemas
import hashlib

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = models.User(
        user_id=user.user_id,
        password=hashed_pw,
        name=user.name
    )
    db.add(db_user) # 현재 세션에 추가. INSERT는 되지 않음
    db.commit() # DB에 영구 반영영
    db.refresh(db_user) # 커밋한 객체의 상태를 DB에서 다시 가져옴(created_at)

    return db_user
