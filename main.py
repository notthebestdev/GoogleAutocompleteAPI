import flask
import requests
from urllib.parse import quote
import re
import html
import json

app = flask.Flask(__name__)

# Cache to store search results
search_cache = {}

@app.route('/')
def index():
    # return text
    return "Hello, World!"

@app.route('/api/v1')
def api_v1():
    search = flask.request.args.get('search')
    if search:
        # Check if result is in cache
        if search in search_cache:
            return flask.jsonify(search_cache[search])
            
        url_encoded_search = quote(search)
        response = requests.get(f"https://www.google.com/complete/search?q={url_encoded_search}&client=gws-wiz")
        match = re.search(r'window\.google\.ac\.h\((\[.*?\])\)', response.text)
        if match:
            suggestions_data = match.group(1)

            # Decode unicode escapes
            suggestions_data = suggestions_data.encode().decode('unicode_escape')

            # Convert to Python object
            data = json.loads(suggestions_data)

            # Extract suggestions (they're in data[0])
            suggestions = [html.unescape(re.sub(r'<.*?>', '', item[0])) for item in data[0]]
            
            # Store in cache and return
            search_cache[search] = suggestions
            return flask.jsonify(suggestions)

    # Return an empty list if no search term is provided
    return flask.jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)