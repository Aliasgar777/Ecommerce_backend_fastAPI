from fastapi import FastAPI
from pydantic import BaseModel
from .core.database import Base, engine
from .core.logger import logger

app = FastAPI()

@app.get("/")
def root():
    logger.info("root endpoint called")
    return "Helooo"


"""
Only uncomment below to create new tables
"""
# Base.metadata.create_all(bind = engine)