import time
import logging
from fastapi import Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("logistics_logger")


async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Completed: {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.4f}s")
    return response