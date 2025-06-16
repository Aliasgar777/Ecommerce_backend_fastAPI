from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from .logger import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit= False ,autoflush=False, bind = engine)

def get_db():
    db = SessionLocal()
    try:
        logger.debug("Database session opened.")
        yield db
    except Exception as e:
        logger.critical(f"Exception occurred during DB session : {e}")
        raise e
    finally:
        db.close()
        logger.debug("Database session closed.")

Base = declarative_base()