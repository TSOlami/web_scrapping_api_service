from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the MySQL connection string
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DB}"

# Initialize SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Scholarship table
class Scholarship(Base):
    __tablename__ = 'scholarships'
    id = Column(Integer, primary_key=True, index=True)
    program_title = Column(String(255), nullable=False)
    funded_by = Column(String(255), nullable=True)
    url = Column(String(500), nullable=False)
    deadline = Column(DateTime, nullable=True)
    requirements = Column(JSON, nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    degree_level = Column(Enum('bachelor', 'master', 'doctorate', name='degree_level'), nullable=True)
    times_updated = Column(Integer, nullable=True, default=0)


# Define the News table
class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    image_url = Column(String(500), nullable=True)
    source = Column(String(255), nullable=True)
    url = Column(String(500), nullable=True)
    category = Column(Enum('visa', 'blog', name='news_category'), nullable=False)
    times_updated = Column(Integer, nullable=True, default=0)

# Create all tables
Base.metadata.create_all(bind=engine)
