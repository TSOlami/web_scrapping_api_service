import json
import time
import random
from requests.exceptions import RequestException
from scrapegraphai.graphs import SmartScraperGraph
import logging
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .models import Scholarship

# Load environment variables
load_dotenv()

# Define the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

def scrape_site(site, db: Session, retries=3):
    """Scrape the given site and save the result to the database."""
    for attempt in range(retries):
        try:
            logging.info(f"Starting scraping process for {site} (Attempt {attempt+1})")

            # Define the configuration for the scraping pipeline
            graph_config = {
                "llm": {
                    "api_key": OPENAI_API_KEY,
                    "model": "openai/gpt-3.5-turbo",
                    "temperature": 0,
                },
                "verbose": True,
                "headless": True,
                "browser_type": "playwright"
            }

            # Create the SmartScraperGraph instance
            smart_scraper_graph = SmartScraperGraph(
                prompt="List me all the master's scholarships available in Canada with their respective Program titles, Managed / Funded by, URLs, deadlines, and requirements.",
                source=site,
                config=graph_config
            )

            # Run the pipeline to scrape data
            articles_data = smart_scraper_graph.run()

            # Save the result to the MySQL database
            for article in articles_data:
                # Create a new Scholarship entry
                scholarship = Scholarship(
                    program_title=article.get('program_title'),
                    funded_by=article.get('funded_by'),
                    url=article.get('url'),
                    deadline=article.get('deadline'),
                    requirements=article.get('requirements')
                )

                # Add the scholarship record to the session
                db.add(scholarship)

            # Commit the transaction to save data in the DB
            db.commit()
            
            logging.info(f"Successfully scraped and saved data from {site}")
            break  # Break out of the retry loop if successful

        except RequestException as e:
            logging.error(f"Request error while scraping {site} on attempt {attempt+1}: {e}")
            time.sleep(random.uniform(1, 3))  # Delay before retry

        except Exception as e:
            logging.error(f"General error occurred while scraping {site}: {e}")
            break
