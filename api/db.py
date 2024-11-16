from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings
import logging

settings = get_settings()

# Add logging for database connection
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Add SSL requirement for Render PostgreSQL
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True,  # Enable SQL logging
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    logger.info("Database connection successful")
except Exception as e:
    logger.error(f"Database connection failed: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
