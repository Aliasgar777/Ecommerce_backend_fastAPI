from fastapi import FastAPI
from pydantic import BaseModel
from .core.database import Base, SessionLocal, engine
from .core.logger import logger
from .auth.models import Users

app = FastAPI()


@app.get("/")
def root():
    logger.info("root endpoint called")
    return "hellooo, its me"


"""
Only uncomment below to create new tables
"""
Base.metadata.create_all(bind = engine)