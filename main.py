
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
import requests
from urllib.parse import quote
import re
import html
import json
from typing import List, Optional

app = FastAPI()

# Cache to store search results
search_cache = {}

@app.get("/")
def index():
    # redirect users to /docs
    return RedirectResponse(url='/docs')

@app.get("/api/v1", response_model=List[str])
def api_v1(search: Optional[str] = Query(None)):
    if search:
        # Check if result is in cache
        if search in search_cache:
            return search_cache[search]
            
        url_encoded_search = quote(search)
        response = requests.get(f"https://www.google.com/complete/search?q={url_encoded_search}&client=gws-wiz")
        match = re.search(r'window\.google\.ac\.h\((\[.*?\])\)', response.text)
        if match:
            suggestions_data = match.group(1)
            suggestions_data = suggestions_data.encode().decode('unicode_escape')
            data = json.loads(suggestions_data)
            suggestions = [html.unescape(re.sub(r'<.*?>', '', item[0])) for item in data[0]]
            
            # Store in cache and return
            search_cache[search] = suggestions
            return suggestions

    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
