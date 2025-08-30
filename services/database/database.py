# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.domain.base import Base

DATABASE_URL = str(os.getenv("DATABASE_URL", "postgresql+psycopg2://admin:admin123@localhost:5432/syriagpt"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()