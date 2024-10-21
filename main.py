import asyncio
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
from app.database import get_db
from app.scraper import scrape_site
from app.models import Scholarship
from app.schemas import ScholarshipBase
import logging

app = FastAPI()

# List of websites to scrape
websites = [
    "https://yconic.com",
    # "https://scholarshipscanada.com",
    # "https://www.scholarshipca.com/scholarships-in-canada-2025-2026-for-international-students",
    # "https://greatyop.com/destination/canada/",
    # "https://scholarshipscanada.com/Scholarships/FeaturedScholarships.aspx",
    # "https://www.educanada.ca/scholarships-bourses/index.aspx?lang=eng",
    # "https://www.scholarships.com/financial-aid/college-scholarships/scholarships-by-state/canada-scholarships/",
    # "https://studentawards.com/scholarships/",
    # "https://opportunitydesk.org/2024/09/01/canada-scholarships/",
    # "https://scholarships360.org/scholarships/study-in-canada-scholarships/",
    # "https://scholartree.ca/scholarships/for/international-students"
]

def run_scraper():
    """Run the scraper for all sites and use a DB session."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        db: Session = next(get_db())  # Create a DB session
        executor.map(lambda site: scrape_site(site, db), websites)

@app.get("/")
def read_root():
    """Welcome message for the API."""
    return {"message": "Welcome to the Scholarships API!"}

@app.get("/health/")
def health_check():
    """Health check endpoint for the API."""
    return {
        "message": "API is healthy!",
        "status": "ok"
    }

@app.get("/scholarships/", response_model=list[ScholarshipBase])
def get_scholarships(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve a list of scholarships with optional pagination."""
    scholarships = db.query(Scholarship).offset(skip).limit(limit).all()
    return scholarships

@app.get("/scholarships/{scholarship_id}", response_model=ScholarshipBase)
def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    """Retrieve a single scholarship by ID."""
    scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    
    return scholarship

@app.get("/start-scraping/")
def start_scraping(background_tasks: BackgroundTasks):
    """Start the scraping process in the background."""
    background_tasks.add_task(run_scraper)
    return {"message": "Scraping started in the background."}

# Configure logging
logging.basicConfig(level=logging.INFO)

# Start Uvicorn server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
