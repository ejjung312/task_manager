from fastapi import Depends, HTTPException, BackgroundTasks, Query, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import user as user_crud
from app.models import user as user_model

from . import service, schemas, email_utils

router = APIRouter(tags=["Auth"])

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = service.decode_access_token(token) # 토큰이 만료되면 자동으로 JWTError 발생
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_crud.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, form_data.username)
    if not user or not service.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = service.create_access_token({"sub": user.user_id})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user


@router.post("/register")
async def register(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(user_model.User).filter_by(user_id=user.user_id).first():
        raise HTTPException(status_code=400, detail="User Id already exists")

    user.create_user(db, user)

    token = service.create_email_token(user.email)
    # BackgroundTasks - 백그라운드 작업
    background_tasks.add_task(email_utils.send_verification_email, user.email, token)
    
    return {"message": "회원가입 완료. 이메일 인증 링크를 확인하세요."}

@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        email = service.verify_email_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다.")
    
    user = db.query(user_model.User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    user.is_verified = True
    db.commit()
    return {"message": "이메일 인증이 완료되었습니다."}