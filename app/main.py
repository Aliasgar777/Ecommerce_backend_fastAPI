from fastapi import FastAPI
from pydantic import BaseModel
from .core.logger import logger
from .auth.models import Users
from app.auth.routes import router 

app = FastAPI()

@app.get("/")
def root():
    logger.info("root endpoint called")
    return "hellooo, its me"

app.include_router(router, tags=["Auth"])