
# Google Search Suggestions API

A FastAPI-based REST API that provides Google search suggestions with caching functionality.

## Features

- Fetch real-time Google search suggestions
- In-memory caching for faster repeated queries
- RESTful API endpoint
- FastAPI with automatic OpenAPI documentation

## API Endpoints

### Root Endpoint
- URL: `/`
- Method: `GET`
- Response: Redirects you to /docs

### Search Suggestions
- URL: `/api/v1`
- Method: `GET`
- Query Parameter: `search` (required)
- Response: List of search suggestions based on the query

## Usage

1. Start the server:
```bash
python main.py
```

2. The server will run at `http://0.0.0.0:5000`

3. Access the API documentation at:
- Swagger UI: `http://0.0.0.0:5000/docs`
- ReDoc: `http://0.0.0.0:5000/redoc`

## Example Request

```
GET /api/v1?search=python
```

Response:
```json
[
  "python compiler",
  "python",
  "python download",
  "python online compiler",
  "python programming",
  "python tutorial",
  "python interview questions",
  "python install",
  "python libraries",
  "python snake"
]
```
