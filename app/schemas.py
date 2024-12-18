from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScholarshipBase(BaseModel):
    id: int
    program_title: str
    funded_by: Optional[str] = None
    url: str
    deadline: Optional[datetime] = None
    requirements: Optional[List[str]] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
