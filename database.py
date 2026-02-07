"""
Database configuration and setup
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

# SQLite database (use an absolute path so the DB file is consistent across restarts)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "wardrobe.db"
# Ensure path uses forward slashes for the sqlite URL on all platforms
DB_URL_PATH = str(DB_PATH).replace("\\", "/")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_URL_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)

