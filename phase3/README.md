# Phase 3: Filtering & LLM Integration (Groq)

Filter cleaned restaurant data by place, rating, price, and cuisine; call Groq LLM to produce ranked recommendations.

## Structure

- `src/filter.py` — `filter_by_criteria()` (place, min_rating, max_price, cuisine)
- `src/prompts.py` — `build_recommendation_prompt()`, `system_prompt()`
- `src/groq_client.py` — `get_completion()` (Groq chat API, `GROQ_API_KEY` from env)
- `src/service.py` — `get_recommendations()` (single entrypoint: filter → prompt → LLM → parse)

## Setup

```bash
cd phase3
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your Groq API key (required for real recommendations):

```bash
export GROQ_API_KEY=your_key_here
# or copy .env.example to .env and set GROQ_API_KEY there (use python-dotenv in your app)
```

## Run tests

**Without API key** (unit tests only; integration tests are skipped):

```bash
cd phase3 && pip install -r requirements.txt && python -m pytest tests/ -v
```

**With API key** (run all tests, including real Groq calls):

```bash
export GROQ_API_KEY=your_key_here
cd phase3 && python -m pytest tests/ -v
```

To confirm everything works before connecting Groq:

```bash
cd phase3 && python -m pytest tests/ -v
```

After connecting the Groq API key, run the same command to execute integration tests as well.

## Usage

`get_recommendations` expects **cleaned rows** from Phase 2 (each row has `rating`, `price`, `cuisines` and a place column such as `location`). You can produce these by running Phase 1 (fetch) and Phase 2 (clean), then passing the result here.

```python
from src.service import get_recommendations

# cleaned_rows = ... from Phase 2 run_pipeline()
result = get_recommendations(
    cleaned_rows,
    place="Bangalore",
    rating=4.0,
    price=1000,           # optional
    cuisine="North Indian",  # optional
    place_column="location",  # key in rows for location
    name_key="name",      # key for restaurant name
)

# result["recommendations"] -> [{"name": "...", "reason": "..."}, ...]
# result["raw_response"]    -> full LLM text
# result["candidates_count"] -> number of restaurants sent to LLM
```

## Test cases and API key

- **Unit tests** (filter, prompts, service with mocked Groq, response parsing) run **without** `GROQ_API_KEY`.
- **Integration tests** (`test_get_completion_integration_real`, `test_get_recommendations_integration_real_groq`) are **skipped** when `GROQ_API_KEY` is not set.
- After you connect your Groq API key (env or `.env`), run `pytest tests/ -v` again to execute these integration tests and confirm end-to-end behavior.
