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
    degree_level: Optional[str] = None
    times_updated: Optional[int] = 0

    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    body:Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    category: str
    times_updated: Optional[int] = 0

    class Config:
        from_attributes = True