from sqlalchemy.orm import Session
from .models import SessionLocal
import logging


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
        logging.info("Database connection successful")
    finally:
        db.close()
