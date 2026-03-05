"""
Tests for data loader. No API key or network required.
"""

import csv
import tempfile
from pathlib import Path

import pytest
from src.data_loader import load_cleaned_data


def test_load_cleaned_data_empty_when_no_path():
    assert load_cleaned_data() == []
    assert load_cleaned_data(path=None) == []


def test_load_cleaned_data_from_csv():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["location", "name", "rating", "price", "cuisines"])
        w.writeheader()
        w.writerow({"location": "Bangalore", "name": "R1", "rating": "4.5", "price": "500", "cuisines": "North Indian, Chinese"})
        w.writerow({"location": "Mumbai", "name": "R2", "rating": "4.0", "price": "800", "cuisines": "Cafe"})
        path = f.name
    try:
        rows = load_cleaned_data(path=path)
        assert len(rows) == 2
        assert rows[0]["location"] == "Bangalore"
        assert rows[0]["name"] == "R1"
        assert rows[0]["rating"] == 4.5
        assert rows[0]["price"] == 500
        assert rows[0]["cuisines"] == ["North Indian", "Chinese"]
        assert rows[1]["cuisines"] == ["Cafe"]
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_cleaned_data_nonexistent_path():
    assert load_cleaned_data(path="/nonexistent/cleaned.csv") == []
