# Phase 1: Project Setup & Data Access

Reproducible environment and access to the Zomato restaurant recommendation dataset from Hugging Face.

## Structure

- `src/` — Fetch module (`fetch_dataset.py`)
- `data/` — Optional cache/output for dataset artifacts
- `tests/` — Tests for fetch logic
- `config/` — Config placeholders
- `requirements.txt` — Dependencies
- `.env.example` — Example env vars (e.g. `HF_TOKEN`)

## Setup

```bash
cd phase1
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional: copy `.env.example` to `.env` and set `HF_TOKEN` if the dataset is gated.

## Run tests

From **phase1** directory (recommended):

```bash
cd phase1
pip install -r requirements.txt
python -m pytest tests/test_fetch_dataset.py -v
```

From **project root**:

```bash
cd phase1 && pip install -r requirements.txt && python -m pytest tests/test_fetch_dataset.py -v
```

**To confirm everything is working**, run:

```bash
cd phase1 && python -m pytest tests/test_fetch_dataset.py -v
```

(Ensure dependencies are installed first: `pip install -r requirements.txt`.)

First run may take 1–2 minutes while the dataset is downloaded from Hugging Face; the cache is stored under `phase1/data/hf_cache`.

## Usage

```python
from src.fetch_dataset import fetch_dataset

# Load full dataset
ds = fetch_dataset()

# Load a small sample (e.g. for quick checks)
ds = fetch_dataset(sample_size=100)
```
