import json
import time
import random
from requests.exceptions import RequestException
from scrapegraphai.graphs import SmartScraperGraph
import logging
import os
from dotenv import load_dotenv

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

def scrape_site(site, retries=3):
    """
    Scrape the given site and handle retries if errors occur.
    """
    for attempt in range(retries):
        try:
            logging.info(f"Starting scraping process for {site} (Attempt {attempt+1})")

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

            # Create the scraper object and run it
            smart_scraper_graph = SmartScraperGraph(
                prompt="List me all the master's scholarships available in Canada with their respective Program titles, Managed / Funded by, URLs, deadlines, and requirements.",
                source=site,
                config=graph_config
            )

            articles_data = smart_scraper_graph.run()
            print("Articles Data:", articles_data)

            # Save results
            site_name = site.replace('https://', '').replace('.', '_')
            with open(f'{site_name}_scholarships.json', 'w') as json_file:
                json.dump(articles_data, json_file, indent=4)

            logging.info(f"Successfully scraped {site}")
            break  # Break if successful

        except RequestException as e:
            logging.error(f"Request error while scraping {site} on attempt {attempt+1}: {e}")
            time.sleep(random.uniform(1, 3))  # Adding delay to avoid IP blocks

        except Exception as e:
            logging.error(f"General error occurred while scraping {site}: {e}")
            break
