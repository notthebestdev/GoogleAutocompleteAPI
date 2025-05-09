from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import quote
import re
import html
import json
from typing import List, Optional

app = FastAPI(
    title="Google Autocomplete API",
    description=
    "A FastAPI service that provides Google search suggestions with caching functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc")

search_cache = {}

# Rate limiter configuration
RATE_LIMIT_DURATION = timedelta(minutes=1)  # Time window
RATE_LIMIT_REQUESTS = 25  # Maximum requests per window


class RateLimiter:

    def __init__(self):
        self.requests = defaultdict(list)

    def is_rate_limited(self, ip: str) -> bool:
        now = datetime.now()
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if now - req_time < RATE_LIMIT_DURATION
        ]

        if len(self.requests[ip]) >= RATE_LIMIT_REQUESTS:
            return True

        self.requests[ip].append(now)
        return False


rate_limiter = RateLimiter()


@app.get("/", description="Redirects to API documentation")
def index():
    return RedirectResponse(url='/docs')


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api"):
        client_ip = request.client.host if request.client else "unknown"
        if rate_limiter.is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail":
                    f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_DURATION.seconds // 60} minutes."
                })
    return await call_next(request)


@app.get("/api/v1",
         response_model=List[str],
         description="Get Google search suggestions for a given search term",
         summary="Retrieve search suggestions",
         response_description="List of search suggestions based on the query")
def api_v1(search: str = Query(
    ..., description="Search term to get suggestions for (required)")):
    # search parameter is now required, no need to check if it exists
        # Check if result is in cache
        if search in search_cache:
            return search_cache[search]

        url_encoded_search = quote(search)
        response = requests.get(
            f"https://www.google.com/complete/search?q={url_encoded_search}&client=gws-wiz"
        )
        match = re.search(r'window\.google\.ac\.h\((\[.*?\])\)', response.text)
        if match:
            suggestions_data = match.group(1)
            suggestions_data = suggestions_data.encode().decode(
                'unicode_escape')
            data = json.loads(suggestions_data)
            suggestions = [
                html.unescape(re.sub(r'<.*?>', '', item[0]))
                for item in data[0]
            ]

            # Store in cache and return
            search_cache[search] = suggestions
            return suggestions

        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
