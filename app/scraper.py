import time
from datetime import datetime
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

def parse_date(date_str):
    try:
        # Parse the string date in 'YYYY-MM-DD' format to a datetime object
        return datetime.strptime(date_str, "%Y-%m-%d").date()  # Converts to YYYY-MM-DD format
    except ValueError as e:
        logging.error(f"Date parsing error: {e}")
        return None

def scrape_site(site, db: Session, retries=1):
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
            prompt=(
                    "List all the master's scholarships available in Canada with their "
                    "respective Program titles, Managed/Funded by (optional), URLs, deadlines, and requirements(optional, list them as separate items). "
                    "Strictly respond **only** in valid JSON format with the following structure and nothing else: "
                    "{ \"program_title\": \"string\", \"funded_by\": \"string\", \"url\": \"string\", \"deadline\": \"YYYY-MM-DD\", \"requirements\": [\"string1\", \"string2\", ...] }. "
                    "Do not include any extra text, explanations, or comments, just valid JSON."
                ),
                source=site,
                config=graph_config
            )

            # Run the pipeline to scrape data
            articles_data = smart_scraper_graph.run()

            logging.info(f"Scraped {len(articles_data)} scholarships from {site}")

            logging.info(f"Articles data: {articles_data}")

            # Handle case where articles_data is a single dictionary
            if isinstance(articles_data, dict):
                # If it's a single dictionary, wrap it in a list
                articles_data = [articles_data]

            # Validate articles_data is now a list of dictionaries
            if isinstance(articles_data, list):
                # Save the result to the MySQL database
                for article in articles_data:

                    # Check if the article data is a dictionary
                    if not isinstance(article, dict):
                        logging.error(f"Expected a dictionary but got: {article}")
                        return

                    # Create a new Scholarship entry
                    scholarship = Scholarship(
                        program_title=article.get('program_title'),
                        funded_by=article.get('funded_by'),
                        url=article.get('url'),
                        deadline=parse_date(article.get('deadline')),
                        requirements=article.get('requirements')
                    )

                    # Add the scholarship record to the session
                    db.add(scholarship)
                    logging.info(f"Added scholarship: {scholarship.program_title} from {site}")

                # Commit the transaction to save data in the DB
                db.commit()
                
                logging.info(f"Successfully scraped and saved data from {site}")

            else:
                logging.error(f"Expected list or dictionary but got: {type(articles_data)}")

        except RequestException as e:
            logging.error(f"Request error while scraping {site} on attempt {attempt+1}: {e}")
            time.sleep(random.uniform(1, 3))  # Delay before retry

        except Exception as e:
            logging.error(f"General error occurred while scraping {site}: {e}")
            break
