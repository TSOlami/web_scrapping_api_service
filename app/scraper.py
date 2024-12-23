import time
from datetime import datetime
import random
from requests.exceptions import RequestException
from scrapegraphai.graphs import SmartScraperGraph
import logging
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .models import Scholarship, News

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
            logging.info(f"Starting scraping process for {site} (Attempt {attempt + 1})")

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
                    "Extract all scholarships available from the given site with their details, "
                    "including Program title, Managed/Funded by (optional), Degree level, URL, Deadline, and Requirements (optional). "
                    "Strictly reply only with a valid JSON list containing all scholarships on the page. "
                    "Each JSON object should have the following structure: "
                    "[{ "
                    "\"program_title\": \"string\", "
                    "\"funded_by\": \"string\", "
                    "\"degree_level\": \"string\", "
                    "\"url\": \"string\", "
                    "\"deadline\": \"YYYY-MM-DD\", "
                    "\"requirements\": [\"string1\", \"string2\", ...] "
                    "}, ...]. "
                    "Ensure that the 'degree_level' is either 'bachelor', 'master', or 'doctorate'. "
                    "Include all scholarships on the page, and do not return only the first one. "
                    "Do not add any extra text, explanations, or comments."
                ),
                source=site,
                config=graph_config
            )

            # Run the scraping pipeline
            scholarships_data = smart_scraper_graph.run()

            logging.info(f"Raw scraped data: {scholarships_data}")

            # Normalize data to ensure it's a list of dictionaries
            if isinstance(scholarships_data, dict):
                scholarships_data = [scholarships_data]
            elif not isinstance(scholarships_data, list):
                logging.error(f"Unexpected data format: {type(scholarships_data)}")
                scholarships_data = []

            logging.info(f"Normalized scholarships data: {scholarships_data}")

            # Save data to the database
            for scholarship in scholarships_data:
                if not isinstance(scholarship, dict):
                    logging.error(f"Invalid scholarship data format: {scholarship}")
                    continue

                # Check for duplicate scholarships
                existing_scholarship = db.query(Scholarship).filter(
                    Scholarship.program_title == scholarship.get('program_title')
                ).first()

                if not existing_scholarship:
                    # Create a new Scholarship entry
                    new_scholarship = Scholarship(
                        program_title=scholarship.get('program_title'),
                        funded_by=scholarship.get('funded_by'),
                        degree_level=scholarship.get('degree_level'),
                        url=scholarship.get('url'),
                        deadline=parse_date(scholarship.get('deadline')),
                        requirements=scholarship.get('requirements')
                    )

                    db.add(new_scholarship)
                    logging.info(f"Added scholarship: {new_scholarship.program_title} from {site}")
                else:
                    logging.info(f"Scholarship already exists: {existing_scholarship.program_title} from {site}")

            # Commit the transaction
            db.commit()
            logging.info(f"Successfully scraped and saved data from {site}")

        except RequestException as e:
            logging.error(f"Request error while scraping {site} on attempt {attempt + 1}: {e}")
            time.sleep(random.uniform(1, 3))  # Delay before retry

        except Exception as e:
            logging.error(f"General error occurred while scraping {site}: {e}")
            break


def scrape_news_site(site, db: Session, retries=1):
    """Scrape the given news site and save the result to the database."""
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
                    "Extract all news articles from the given news site, including the title, description, published date, source, URL, and category. "
                    "Respond strictly in a valid list of JSON objects with the following structure: "
                    "[{ \"title\": \"string\", \"description\": \"string\", \"published_at\": \"YYYY-MM-DD\", \"source\": \"string\", \"url\": \"string\", \"category\": \"string\" }, ...]. "
                    "Ensure that all articles on the page are included, and do not limit the response to just one article. "
                    "Each JSON object must correspond to a unique article on the page."
                ),
                source=site,
                config=graph_config
            )

            # Run the pipeline to scrape data
            articles_data = smart_scraper_graph.run()

            logging.info(f"Scraped data: {articles_data}")

            # Normalize to ensure `articles_data` is a list
            if isinstance(articles_data, dict):
                articles_data = [articles_data]  # Wrap single dictionary in a list
            elif not isinstance(articles_data, list):
                logging.error(f"Invalid data format: {type(articles_data)}. Expected list.")
                articles_data = []  # Default to an empty list

            # Process articles if the list is not empty
            if articles_data:
                for article in articles_data:
                    if not isinstance(article, dict):
                        logging.error(f"Invalid article format: {article}. Skipping.")
                        continue

                    # Check for duplicate news articles
                    existing_news = db.query(News).filter(News.title == article.get('title')).first()
                    if not existing_news:
                        news = News(
                            title=article.get('title'),
                            description=article.get('description'),
                            published_at=parse_date(article.get('published_at')),
                            source=article.get('source'),
                            url=article.get('url'),
                            category=article.get('category')
                        )
                        db.add(news)
                        logging.info(f"Added news: {news.title} from {site}")
                    else:
                        logging.info(f"News already exists: {existing_news.title} from {site}")

                db.commit()
                logging.info(f"Successfully scraped and saved data from {site}")
            else:
                logging.warning(f"No valid articles found from {site}.")

        except RequestException as e:
            logging.error(f"Request error while scraping {site} on attempt {attempt+1}: {e}")
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            logging.error(f"General error occurred while scraping {site}: {e}")
            break

def fetch_description(url, db, scholarship_id, is_requirement_null=False, is_degree_level_null=False, retries=1):
    """
    Fetch the description (and optionally requirements or degree level) from the given URL and save it to the database.
    """
    for attempt in range(retries):
        try:
            # Define the configuration for the scraping pipeline
            graph_config = {
                "llm": {
                    "api_key": OPENAI_API_KEY,
                    "model": "openai/gpt-3.5-turbo",
                    "temperature": 0,
                },
                "verbose": True,
                "headless": True,
                "browser_type": "playwright",
            }

            # Adjust prompt based on the flags
            if is_requirement_null and is_degree_level_null:
                prompt = (
                    "Extract the description, requirements, and degree level of the scholarship from the given URL. "
                    "Strictly respond **only** in valid JSON format with the following structure and nothing else: "
                    "{ \"description\": \"string\", \"requirements\": [\"string1\", \"string2\", ...], \"degree_level\": \"string\" }. "
                    "Degree level must be 'bachelor', 'master', or 'doctorate'. If not specified, leave it as null. "
                    "Do not include any extra text, explanations, or comments, just valid JSON."
                )
            elif is_requirement_null:
                prompt = (
                    "Extract the description and requirements of the scholarship from the given URL. "
                    "Strictly respond **only** in valid JSON format with the following structure and nothing else: "
                    "{ \"description\": \"string\", \"requirements\": [\"string1\", \"string2\", ...] }. "
                    "Do not include any extra text, explanations, or comments, just valid JSON."
                )
            elif is_degree_level_null:
                prompt = (
                    "Extract the description and degree level of the scholarship from the given URL. "
                    "Strictly respond **only** in valid JSON format with the following structure and nothing else: "
                    "{ \"description\": \"string\", \"degree_level\": \"string\" }. "
                    "Degree level must be 'bachelor', 'master', or 'doctorate'. If not specified, leave it as null. "
                    "Do not include any extra text, explanations, or comments, just valid JSON."
                )
            else:
                prompt = (
                    "Extract the description of the scholarship from the given URL. "
                    "Strictly respond **only** in valid JSON format with the following structure and nothing else: "
                    "{ \"description\": \"string\" }. "
                    "Do not include any extra text, explanations, or comments, just valid JSON."
                )

            logging.info(f"Fetching data from {url} (Attempt {attempt + 1})")

            # Create and run the SmartScraperGraph instance
            smart_scraper_graph = SmartScraperGraph(prompt=prompt, source=url, config=graph_config)
            description_data = smart_scraper_graph.run()

            # Extract data
            description = description_data.get("description", "").strip()
            requirements = description_data.get("requirements", []) if is_requirement_null else None
            degree_level = description_data.get("degree_level") if is_degree_level_null else None

            if description or requirements or degree_level:
                # Save data to the database
                scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
                if scholarship:
                    scholarship.description = description
                    if requirements is not None:
                        scholarship.requirements = requirements
                    if degree_level in ['bachelor', 'master', 'doctorate']:
                        scholarship.degree_level = degree_level  # Update only valid degree levels
                    db.commit()
                    logging.info(f"Data saved for scholarship {scholarship_id}")

            return description_data

        except RequestException as e:
            logging.error(f"Error fetching data from {url} on attempt {attempt + 1}: {e}")
            time.sleep(random.uniform(1, 3))  # Retry delay

        except Exception as e:
            logging.error(f"Unexpected error fetching data from {url}: {e}")

    logging.error(f"Failed to fetch data from {url} after {retries} attempts")
    return None

def fetch_body(url, db, news_id, retries=1):
    """
    Fetch the body content from the given news URL and save it to the database.
    """
    for attempt in range(retries):
        try:
            # Define the configuration for the scraping pipeline
            graph_config = {
                "llm": {
                    "api_key": OPENAI_API_KEY,
                    "model": "openai/gpt-3.5-turbo",
                    "temperature": 0,
                },
                "verbose": True,
                "headless": True,
                "browser_type": "playwright",
            }

            prompt = (
                "Extract the body content of the news article from the given URL. "
                "Strictly respond **only** in valid JSON format with the following structure and nothing else: "
                "{ \"body\": \"string\" }. "
                "Do not include any extra text, explanations, or comments, just valid JSON."
            )

            logging.info(f"Fetching data from {url} (Attempt {attempt + 1})")

            # Create and run the SmartScraperGraph instance
            smart_scraper_graph = SmartScraperGraph(prompt=prompt, source=url, config=graph_config)
            body_data = smart_scraper_graph.run()

            # Extract data
            body = body_data.get("body", "").strip()

            if body:
                # Save data to the database
                news = db.query(News).filter(News.id == news_id).first()
                if news:
                    news.body = body
                    db.commit()
                    logging.info(f"Data saved for news article {news_id}")

            return body_data

        except RequestException as e:
            logging.error(f"Error fetching data from {url} on attempt {attempt + 1}: {e}")
            time.sleep(random.uniform(1, 3))  # Retry delay

    logging.error(f"Failed to fetch data from {url} after {retries} attempts")
    return None
