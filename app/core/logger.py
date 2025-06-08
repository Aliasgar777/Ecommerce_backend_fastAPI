import logging

logger = logging.getLogger("ecommerce_backend")
logger.setLevel(logging.DEBUG)


file_handler = logging.FileHandler("logs/app.log")
file_handler.setLevel(logging.DEBUG)

file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger.addHandler(file_handler)