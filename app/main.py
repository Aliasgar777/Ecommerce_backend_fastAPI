from fastapi import FastAPI
from pydantic import BaseModel
from .core.logger import logger
from .auth.models import Users

app = FastAPI()

@app.get("/")
def root():
    logger.info("root endpoint called")
    return "hellooo, its me"

