from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for models
Base = declarative_base()

# Import all models to register them with Base metadata
from .database_models import *  # noqa: F401, F403

# Database URL - using SQLite for now, can be changed to PostgreSQL
DATABASE_URL = "sqlite:///./archaeoscan.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()