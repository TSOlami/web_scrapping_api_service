from pydantic import BaseModel
from typing import Optional

class ScholarshipBase(BaseModel):
    program_title: str
    funded_by: Optional[str] = None
    url: str
    deadline: Optional[str] = None
    requirements: Optional[str] = None

    class Config:
        from_attributes = True  # Enable ORM mode to work with SQLAlchemy models
