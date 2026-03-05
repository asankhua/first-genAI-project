#!/usr/bin/env python3
"""
End-to-end integration test: User Input -> API -> (Phase 3) -> Response -> structure.

Uses fixture data and mocked Phase 3 so no Groq or HF download required.
Run from repo root: python scripts/e2e_test.py
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Add phase4 for FastAPI app and TestClient
phase4 = REPO_ROOT / "phase4"
if phase4.exists() and str(phase4) not in sys.path:
    sys.path.insert(0, str(phase4))

# Fixture: minimal cleaned rows (Phase 2 output shape) for Phase 3/4
FIXTURE_CLEANED_ROWS = [
    {
        "location": "Bangalore",
        "name": "Restaurant One",
        "rating": 4.5,
        "price": 600,
        "cuisines": ["North Indian", "Chinese"],
    },
    {
        "location": "Bangalore",
        "name": "Restaurant Two",
        "rating": 4.2,
        "price": 800,
        "cuisines": ["Cafe"],
    },
]


def test_e2e_api_contract():
    """Verify Phase 4 API accepts request and returns Phase 5–expected shape."""
    from unittest.mock import patch
    from fastapi.testclient import TestClient

    # Patch Phase 4 app to use fixture data and mocked recommendations
    import src.app as app_module
    app_module.CLEANED_ROWS = FIXTURE_CLEANED_ROWS

    mock_result = {
        "recommendations": [
            {"name": "Restaurant One", "reason": "High rating and fits budget."},
            {"name": "Restaurant Two", "reason": "Good for casual dining."},
        ],
        "raw_response": "Mocked LLM response.",
        "candidates_count": 2,
    }

    with patch.object(app_module, "get_recommendations", return_value=mock_result):
        client = TestClient(app_module.app)
        r = client.post(
            "/recommendations",
            json={"place": "Bangalore", "rating": 4.0, "price": 1000, "cuisine": "North Indian"},
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "recommendations" in data
    assert "raw_response" in data
    assert "candidates_count" in data
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["name"] == "Restaurant One"
    assert data["recommendations"][0]["reason"]
    assert data["candidates_count"] == 2
    print("E2E API contract test passed.")


def test_e2e_phase4_data_loader_normalization():
    """Phase 4 data_loader normalizes city -> location, restaurant name -> name."""
    if str(phase4) not in sys.path:
        sys.path.insert(0, str(phase4))
    from src.data_loader import load_cleaned_data
    import csv
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["city", "restaurant name", "rating", "price", "cuisines"])
        w.writeheader()
        w.writerow({"city": "Mumbai", "restaurant name": "Test Place", "rating": "4.0", "price": "500", "cuisines": "Cafe"})
        path = f.name
    try:
        rows = load_cleaned_data(path=path)
        assert len(rows) == 1
        assert rows[0].get("location") == "Mumbai"
        assert rows[0].get("name") == "Test Place"
        print("E2E data_loader normalization test passed.")
    finally:
        Path(path).unlink(missing_ok=True)


def test_e2e_phase4_loads_real_csv_if_present():
    """If phase4/data/cleaned.csv exists, Phase 4 load returns rows with location/name."""
    csv_path = REPO_ROOT / "phase4" / "data" / "cleaned.csv"
    if not csv_path.exists():
        print("(Skipping real CSV test: phase4/data/cleaned.csv not found. Run scripts/e2e_pipeline.py first.)")
        return
    sys.path.insert(0, str(phase4))
    from src.data_loader import load_cleaned_data
    rows = load_cleaned_data(path=str(csv_path))
    assert len(rows) > 0, "CSV should have rows"
    row = rows[0]
    assert "rating" in row and "price" in row and "cuisines" in row
    assert row.get("location") or row.get("city"), "Row should have location or city"
    assert row.get("name") or row.get("restaurant name"), "Row should have name or restaurant name"
    print("E2E real CSV load test passed.")


if __name__ == "__main__":
    test_e2e_phase4_data_loader_normalization()
    test_e2e_api_contract()
    test_e2e_phase4_loads_real_csv_if_present()
    print("All E2E tests passed.")
