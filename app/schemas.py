from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScholarshipBase(BaseModel):
    program_title: str
    funded_by: Optional[str] = None
    url: str
    deadline: Optional[datetime] = None
    requirements: Optional[List[str]] = None

    class Config:
        from_attributes = True  # Enable ORM mode to work with SQLAlchemy models
