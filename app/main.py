from fastapi import FastAPI, Request
from .core.logger import logger
from app.auth.routes import router as auth_router
from app.product.routes import router as product_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as order_router
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

@app.get("/")
def root():
    logger.info("root endpoint called")
    return "Ecommerce Homepage"

app.include_router(auth_router, tags=["Auth"])
app.include_router(product_router, tags=["Product Management"])
app.include_router(cart_router, tags=["Cart management"])
app.include_router(order_router,  tags=["Orders"])

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error occurred")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "code": 500
        }
    )