from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base

from . import models, schemas, crud, auth, email_utils

Base.metadata.create_all(bind=engine)
app = FastAPI()

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
        payload = auth.decode_access_token(token) # 토큰이 만료되면 자동으로 JWTError 발생
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.user_id})

    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/register")
async def register(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(user_id=user.user_id).first():
        raise HTTPException(status_code=400, detail="User Id already exists")

    crud.create_user(db, user)

    token = auth.create_email_token(user.email)
    # BackgroundTasks - 백그라운드 작업
    background_tasks.add_task(email_utils.send_verification_email, user.email, token)
    
    return {"message": "회원가입 완료. 이메일 인증 링크를 확인하세요."}

@app.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        email = auth.verify_email_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다.")
    
    user = db.query(models.User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    user.is_verified = True
    db.commit()
    return {"message": "이메일 인증이 완료되었습니다."}