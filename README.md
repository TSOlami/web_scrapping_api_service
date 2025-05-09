# Scholarship and News Web Scraping API

A powerful AI-driven web scraping service that collects scholarship opportunities and news articles from various websites. The service provides a RESTful API that delivers structured data in JSON format.

## Features

- **AI-Powered Scraping**: Uses OpenAI models (GPT-4o and GPT-3.5-turbo) to intelligently extract structured data from websites
- **Scholarship Information Collection**: Scrapes scholarship details including:
  - Program titles
  - Funding organizations
  - Degree levels (bachelor, master, doctorate)
  - URLs
  - Deadlines
  - Requirements
  - Descriptions
- **News Article Collection**: Gathers news articles with:
  - Titles
  - Descriptions
  - Full body content
  - Publication dates
  - Sources
  - Categories
- **Automated Image Generation**: Creates relevant images for scholarships and news articles using Hugging Face's Stable Diffusion model
- **Background Processing**: Handles scraping and image generation tasks in the background
- **Rate Limiting**: Implements a queue management system to control API request rates
- **Database Storage**: Stores all data in a MySQL database with proper schema management
- **RESTful API**: Provides endpoints to access and manage the collected data
- **Automatic Field Completion**: Detects and fills missing information fields

## Technology Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) for database interactions
- **Alembic**: Database migration tool for SQLAlchemy
- **MySQL**: Database for storing scraped data
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for running the FastAPI application
- **ScrapeGraphAI**: AI-powered web scraping library
- **Playwright**: Browser automation for web scraping
- **Hugging Face API**: For generating images using Stable Diffusion
- **Python-dotenv**: Environment variable management
- **Pillow (PIL)**: Python Imaging Library for image processing
- **Threading and Asyncio**: For concurrent and asynchronous operations

## API Endpoints

### Scholarships
- `GET /scholarships/`: List scholarships with pagination
- `GET /scholarships/{scholarship_id}`: Get a specific scholarship
- `GET /start-scraping-scholarships/`: Start the scraping process
- `POST /fetch-scholarship/null-fields/`: Fill in missing fields for scholarships
- `POST /generate-images/scholarships/`: Generate images for scholarships
- `DELETE /scholarships/`: Delete all scholarships
- `DELETE /scholarships/{scholarship_id}`: Delete a specific scholarship
- `DELETE /remove/outdated-scholarships/`: Remove scholarships with passed deadlines

### News
- `GET /news/`: List news articles with pagination
- `GET /news/{news_id}`: Get a specific news article
- `GET /start-news-scraping/`: Start the news scraping process
- `POST /fetch-news/body/`: Fetch missing body content for news articles
- `POST /generate-images/news/`: Generate images for news articles
- `DELETE /news/`: Delete all news articles
- `DELETE /news/{news_id}`: Delete a specific news article

### Misc
- `GET /`: Welcome message
- `GET /health/`: Health check endpoint
- `GET /image-generation-status/{job_id}`: Check status of image generation jobs

## Setup and Installation

1. **Clone the repository**
   ```
   git clone [repository-url]
   cd web_scrapping_api_service
   ```

2. **Set up a virtual environment**
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Create a .env file with the following variables**
   ```
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_HOST=localhost
   MYSQL_DB=your_database_name
   OPENAI_API_KEY=your_openai_api_key
   HF_API_TOKEN=your_huggingface_token
   ```

5. **Run database migrations**
   ```
   alembic upgrade head
   ```

6. **Start the server**
   ```
   python main.py
   ```
   The server will run at http://127.0.0.1:5000

## How It Works

1. The scraper uses AI models to extract structured data from websites
2. Data is processed and stored in a MySQL database
3. Missing fields are detected and filled with additional AI-powered scraping
4. Images are generated based on content titles using Stable Diffusion
5. All data is accessible through the RESTful API endpoints

## Configuration

You can customize the list of websites to scrape by modifying the `websites` and `news_websites` lists in `main.py`.

## Data Models

### Scholarship
- `id`: Unique identifier
- `program_title`: Name of the scholarship program
- `funded_by`: Organization funding the scholarship
- `url`: Link to the scholarship page
- `deadline`: Application deadline date
- `requirements`: List of requirements for the scholarship
- `image_url`: URL to the generated image
- `description`: Detailed description of the scholarship
- `degree_level`: Educational level (bachelor, master, doctorate)
- `times_updated`: Counter for tracking update attempts

### News
- `id`: Unique identifier
- `title`: News article title
- `description`: Brief summary of the article
- `body`: Full content of the article
- `published_at`: Publication date
- `image_url`: URL to the generated image
- `source`: Source of the news
- `url`: Link to the article
- `category`: Article category (visa, blog)
- `times_updated`: Counter for tracking update attempts
