# Phase 4: Backend API

HTTP API for the Zomato AI Restaurant Recommendation service. Exposes POST/GET endpoints that accept place, rating, and optional price/cuisine and return recommendations (via Phase 3 when available).

## Structure

- `src/app.py` — FastAPI app, CORS, `POST /recommendations`, `GET /recommendations`, `GET /health`
- `src/data_loader.py` — Load cleaned rows from CSV (optional; `CLEANED_DATA_PATH` env)
- `src/recommendation_service.py` — Wrapper around Phase 3 `get_recommendations` (or stub if Phase 3 not on path)

## Setup

```bash
cd phase4
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional: set `CLEANED_DATA_PATH` to a CSV of cleaned rows (from Phase 2). If unset, the API still runs but has no data (recommendations will be empty unless Phase 3 stub returns something).

## Run tests

From **phase4** directory:

```bash
python -m pytest tests/ -v
```

From **project root**:

```bash
cd phase4 && pip install -r requirements.txt && python -m pytest tests/ -v
```

**To confirm everything is working:**

```bash
cd phase4 && python -m pytest tests/ -v
```

Tests mock the recommendation service, so no Groq API key or Phase 3 data is required.

## Run the API server

```bash
cd phase4
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

- **OpenAPI (Swagger):** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  
- **POST /recommendations:** JSON body `{ "place": "Bangalore", "rating": 4.0, "price": 1000, "cuisine": "North Indian" }`  
- **GET /recommendations:** `?place=Bangalore&rating=4.0&price=1000&cuisine=North Indian`

## CORS

By default all origins are allowed. To restrict: set `CORS_ORIGINS=http://localhost:3000,https://myui.com` (comma-separated).
