#!/usr/bin/env python3
"""
E2E pipeline: Phase 1 (fetch) -> Phase 2 (clean) -> CSV for Phase 4.

Run from repo root: python scripts/e2e_pipeline.py
Optional: E2E_SAMPLE_SIZE=50 CLEANED_OUTPUT=phase4/data/cleaned.csv
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load root .env (HF_TOKEN, GROQ_API_KEY, etc.)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

# Import from phase1 (src = phase1/src)
phase1_path = str(REPO_ROOT / "phase1")
if phase1_path not in sys.path:
    sys.path.insert(0, phase1_path)
from src.fetch_dataset import fetch_dataset, dataset_to_rows

# Import from phase2 (replace path so src = phase2/src)
sys.path.remove(phase1_path)
# Clear phase1's src from cache so phase2's src is used
for key in list(sys.modules.keys()):
    if key == "src" or key.startswith("src."):
        del sys.modules[key]
phase2_path = str(REPO_ROOT / "phase2")
if phase2_path not in sys.path:
    sys.path.insert(0, phase2_path)
from src.pipeline import run_pipeline, save_cleaned, DEFAULT_COLUMN_MAP


def infer_column_map(first_row: dict) -> dict:
    """Infer Phase 2 column_map from raw row keys (HF dataset may use different names)."""
    m = {}
    keys_lower = {k.lower(): k for k in first_row}
    if "rate" in keys_lower:
        m["rating"] = keys_lower["rate"]
    elif "rating" in keys_lower:
        m["rating"] = keys_lower["rating"]
    for k in keys_lower:
        if "cost" in k or "price" in k:
            m["price"] = keys_lower[k]
            break
    if "cuisines" in keys_lower:
        m["cuisines"] = keys_lower["cuisines"]
    if "cuisine" in keys_lower and "cuisines" not in m:
        m["cuisines"] = keys_lower["cuisine"]
    # Use DEFAULT_COLUMN_MAP for any we didn't infer (exact match)
    for logical, default_col in DEFAULT_COLUMN_MAP.items():
        if logical not in m and default_col in first_row:
            m[logical] = default_col
    return m if len(m) >= 2 else DEFAULT_COLUMN_MAP.copy()


def normalize_for_phase3(rows: list) -> None:
    """Ensure each row has 'location' and 'name' for Phase 3 filter/prompts."""
    for row in rows:
        if not row.get("location"):
            row["location"] = (
                row.get("city")
                or row.get("address")
                or row.get("area")
                or row.get("listed_in(city)")
                or ""
            )
        if not row.get("name"):
            row["name"] = row.get("restaurant name") or row.get("restaurant_name") or "Unknown"


def main():
    # Use full dataset by default (51,717 rows). Set E2E_SAMPLE_SIZE to limit for faster runs.
    _sample = os.environ.get("E2E_SAMPLE_SIZE", "")
    sample_size = int(_sample) if _sample and _sample.isdigit() else None
    output = os.environ.get("CLEANED_OUTPUT") or str(REPO_ROOT / "phase4" / "data" / "cleaned.csv")
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("Phase 1: Fetching dataset...")
    dataset = fetch_dataset(sample_size=sample_size)  # None = full ~51k rows
    raw_rows = dataset_to_rows(dataset)
    if not raw_rows:
        print("No rows from dataset. Aborting.")
        sys.exit(1)

    column_map = infer_column_map(raw_rows[0])
    print("Phase 2: Cleaning (column_map = %s)..." % column_map)
    cleaned = run_pipeline(raw_rows, column_map=column_map)
    if not cleaned:
        print("No rows passed cleaning. Aborting.")
        sys.exit(1)

    normalize_for_phase3(cleaned)
    save_cleaned(cleaned, out_path, format="csv")
    print("E2E data ready: %s (%d rows)" % (out_path, len(cleaned)))


if __name__ == "__main__":
    main()
