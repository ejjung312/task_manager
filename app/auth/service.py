from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..core.config import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

EMAIL_SECRET_KEY = settings.EMAIL_SECRET_KEY

def verify_password(plain_pw, hashed_pw):
    return pwd_context.verify(plain_pw, hashed_pw)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def create_email_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, EMAIL_SECRET_KEY, algorithm=ALGORITHM)

def verify_email_token(token: str):
    payload = jwt.decode(token, EMAIL_SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")