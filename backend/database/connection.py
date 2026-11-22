
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from backend.database.models import Base


# Find project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Create database URL
# Create database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Use cloud database (Neon)
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )
else:
    # Use local PostgreSQL
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# Fix PostgreSQL DateStyle compatibility
@event.listens_for(engine, "connect")
def set_date_style(dbapi_connection, connection_record):
    with dbapi_connection.cursor() as cursor:
        cursor.execute("SET DateStyle TO 'ISO, MDY'")
        cursor.execute("SET TIME ZONE 'UTC'")
    dbapi_connection.commit()


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Test database connection
def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        return result.scalar()


# Create database tables
def create_tables():
    Base.metadata.create_all(bind=engine)
