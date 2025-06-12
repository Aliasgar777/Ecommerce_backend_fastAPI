from fastapi import FastAPI
from pydantic import BaseModel
from .core.logger import logger
from .auth.models import Users
from app.auth.routes import router as auth_router
from app.product.routes import router as product_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as order_router

app = FastAPI()

@app.get("/")
def root():
    logger.info("root endpoint called")
    return "hellooo, its me"

app.include_router(auth_router, tags=["Auth"])
app.include_router(product_router, tags=["Product Management"])
app.include_router(cart_router, tags=["Cart management"])
app.include_router(order_router,  tags=["Orders"])