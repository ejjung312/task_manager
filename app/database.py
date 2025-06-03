from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=True) # echo SQL logging
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()