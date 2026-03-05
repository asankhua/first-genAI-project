# Phase 2: Data Cleaning Pipeline

Reusable, testable cleaning logic for Price, Rating, and Cuisines. Pipeline consumes raw rows (e.g. from Phase 1) and outputs clean records.

## Structure

- `src/cleaners.py` — `clean_price`, `clean_rating`, `clean_cuisines`
- `src/pipeline.py` — `run_pipeline`, `save_cleaned`
- `tests/` — unit tests for cleaners and pipeline

## Setup

```bash
cd phase2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run tests

From **phase2** directory:

```bash
python -m pytest tests/ -v
```

From **project root**:

```bash
cd phase2 && pip install -r requirements.txt && python -m pytest tests/ -v
```

**To confirm everything is working:**

```bash
cd phase2 && python -m pytest tests/ -v
```

## Usage

```python
from src.cleaners import clean_price, clean_rating, clean_cuisines
from src.pipeline import run_pipeline, save_cleaned, DEFAULT_COLUMN_MAP

# Single values
clean_price("1,500")       # -> 1500
clean_rating("4.1/5")      # -> 4.1
clean_cuisines("North Indian, Chinese")  # -> ["North Indian", "Chinese"]

# Batch: list of dicts (e.g. from Phase 1 dataset rows)
raw_rows = [
    {"rate": "4.1/5", "approx_cost(for two people)": "1,500", "cuisines": "North Indian"},
]
column_map = {"price": "approx_cost(for two people)", "rating": "rate", "cuisines": "cuisines"}
clean_rows = run_pipeline(raw_rows, column_map=column_map)

# Optional: persist
save_cleaned(clean_rows, "data/cleaned.csv", format="csv")
```

## Column map

If your dataset uses different column names, pass `column_map` to `run_pipeline`:

```python
run_pipeline(raw_rows, column_map={
    "price": "cost_column",
    "rating": "rating_column",
    "cuisines": "cuisines_column",
})
```
