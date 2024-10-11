import asyncio
import nest_asyncio
nest_asyncio.apply()
from fastapi import FastAPI, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
from app.scraper import scrape_site

app = FastAPI()

# List of websites to scrape
websites = [
    "https://yconic.com",
    "https://scholarshipscanada.com",
    "https://www.scholarshipca.com/scholarships-in-canada-2025-2026-for-international-students",
    "https://greatyop.com/destination/canada/",
    "https://scholarshipscanada.com/Scholarships/FeaturedScholarships.aspx",
    "https://www.educanada.ca/scholarships-bourses/index.aspx?lang=eng",
    "https://www.scholarships.com/financial-aid/college-scholarships/scholarships-by-state/canada-scholarships/",
    "https://studentawards.com/scholarships/",
    "https://opportunitydesk.org/2024/09/01/canada-scholarships/",
    "https://scholarships360.org/scholarships/study-in-canada-scholarships/",
    "https://scholartree.ca/scholarships/for/international-students"

]

# Async function for background tasks
async def scrape_websites_in_background(websites):
    """
    Scrape all websites concurrently using a thread pool.
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [loop.run_in_executor(executor, scrape_site, site) for site in websites]
        await asyncio.gather(*futures)

# FastAPI endpoint to trigger scraping
@app.get("/scrape")
async def scrape(background_tasks: BackgroundTasks):
    """
    API endpoint to start the scraping process.
    """
    background_tasks.add_task(scrape_websites_in_background, websites)
    return {"message": "Scraping started in the background."}

# Endpoint to check scraping status (Optional)
@app.get("/status")
async def status():
    return {"message": "Scraping status: check logs for details."}
