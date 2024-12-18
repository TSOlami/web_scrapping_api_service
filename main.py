import asyncio
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
from app.database import get_db
from app.scraper import scrape_site, fetch_description
from app.models import Scholarship
from app.schemas import ScholarshipBase
import logging
from app.image_generator import generate_image
import os
from app.queue_manager import QueueManager, JobStatus
import time
from typing import List
from fastapi.staticfiles import StaticFiles
from datetime import datetime


# Create necessary directories at startup
os.makedirs("static/images", exist_ok=True)

app = FastAPI()
queue_manager = QueueManager()

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

def run_fetch_description(url):
    """ Run the scraper to get the descritions. """
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(lambda site: fetch_description(site), url)

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
async def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching scholarship {scholarship_id}")
    scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship

@app.get("/start-scraping/")
def start_scraping(background_tasks: BackgroundTasks):
    """Start the scraping process in the background."""
    background_tasks.add_task(run_scraper)
    return {"message": "Scraping started in the background."}

@app.post("/fetch-scholarship/description/")
def fetch_scholarship_description(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Get all scholarships without descriptions
    scholarships = db.query(Scholarship).filter(Scholarship.description == None).all()
    logger.info(f"Found {len(scholarships)} scholarships without descriptions")

    # Process each scholarship in the background
    for scholarship in scholarships:
        background_tasks.add_task(fetch_description, scholarship.url, db, scholarship.id)

    return {"message": "Fetching descriptions started in the background."}

async def process_image_generation(job_id: str, scholarship_id: int, db: Session):
    logger.info(f"Starting image generation process for job {job_id} (Scholarship {scholarship_id})")
    try:
        queue_manager.update_job(job_id, JobStatus.PROCESSING)
        
        scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
        if not scholarship:
            raise Exception(f"Scholarship {scholarship_id} not found")

        prompt = f"An image representing {scholarship.program_title}"
        
        # Wait until we can make a request
        while not queue_manager.can_make_request():
            wait_time = queue_manager.time_until_next_available()
            logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds before next request")
            await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
        
        # Record this request
        queue_manager.record_request()
        logger.info(f"Generating image for scholarship {scholarship_id}")
        
        try:
            image_url = generate_image(prompt, scholarship_id)
            
            # Update scholarship with image URL
            scholarship.image_url = image_url
            db.commit()
            logger.info(f"Successfully generated image for scholarship {scholarship_id}")
            
            queue_manager.update_job(job_id, JobStatus.COMPLETED, image_path=image_url)
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise e

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        queue_manager.update_job(job_id, JobStatus.FAILED, error=str(e))

@app.post("/generate-images/")
async def generate_images_for_scholarships(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> List[dict]:
    logger.info("Received request to generate images for scholarships")
    
    # Get scholarships without images
    scholarships = db.query(Scholarship).filter(Scholarship.image_url == None).all()
    logger.info(f"Found {len(scholarships)} scholarships without images")
    
    job_ids = []
    for scholarship in scholarships:
        job_id = queue_manager.create_job(scholarship.id)
        background_tasks.add_task(
            process_image_generation,
            job_id,
            scholarship.id,
            db
        )
        job_ids.append({"scholarship_id": scholarship.id, "job_id": job_id})
        logger.info(f"Queued job {job_id} for scholarship {scholarship.id}")
    
    return job_ids


@app.get("/image-generation-status/{job_id}")
async def get_generation_status(job_id: str):
    logger.info(f"Checking status for job {job_id}")
    job_status = queue_manager.get_job_status(job_id)
    if not job_status:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status


@app.delete('/remove/outdated-scholarships/')
async def remove_outdated_scholarships(db: Session = Depends(get_db)):
    """Remove scholarships that are outdated."""
    scholarships = db.query(Scholarship).all()
    for scholarship in scholarships:
        if scholarship.deadline and scholarship.deadline < datetime.now():
            db.delete(scholarship)
    db.commit()
    return {"message": "Outdated scholarships removed successfully"}

# Ensure the images directory exists
os.makedirs("images", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Start Uvicorn server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
