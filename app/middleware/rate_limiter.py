import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse

# In-memory store: {ip: [timestamp, ...]}
request_counts: dict = defaultdict(list)

RATE_LIMIT = 60       # max requests
WINDOW_SECONDS = 60   # per 60 seconds


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()

    # Keep only timestamps within the current window
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if now - t < WINDOW_SECONDS
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"success": False, "error": "Too many requests. Please try again later."}
        )

    request_counts[client_ip].append(now)
    return await call_next(request)
