from sqlalchemy.orm import Session
from .models import SessionLocal

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
