"""
Unit tests for pipeline orchestrator (Phase 2.2, 2.4).
"""

import csv
import tempfile
from pathlib import Path

import pytest
from src.pipeline import (
    DEFAULT_COLUMN_MAP,
    run_pipeline,
    save_cleaned,
)


# Use explicit column map in tests so we don't depend on exact HF column names
COL = {"price": "cost", "rating": "rate", "cuisines": "cuisines"}


class TestRunPipeline:
    def test_applies_cleaning_rules(self):
        raw = [
            {"name": "R1", "cost": "1,500", "rate": "4.1/5", "cuisines": "North Indian, Chinese"},
        ]
        out = run_pipeline(raw, column_map=COL)
        assert len(out) == 1
        assert out[0]["price"] == 1500
        assert out[0]["rating"] == 4.1
        assert out[0]["cuisines"] == ["North Indian", "Chinese"]
        assert out[0]["name"] == "R1"

    def test_drops_rows_with_missing_required_rating(self):
        raw = [
            {"name": "R1", "cost": "500", "rate": "4.0", "cuisines": "Cafe"},
            {"name": "R2", "cost": "1000", "rate": None, "cuisines": "Bakery"},
            {"name": "R3", "cost": "800", "rate": "3.5/5", "cuisines": ""},
        ]
        out = run_pipeline(raw, column_map=COL, required_columns=["rating"])
        assert len(out) == 2
        assert out[0]["name"] == "R1"
        assert out[1]["name"] == "R3"

    def test_drops_rows_with_invalid_rating(self):
        raw = [
            {"name": "R1", "rate": "invalid"},
        ]
        out = run_pipeline(raw, column_map=COL)
        assert len(out) == 0

    def test_preserves_original_keys(self):
        raw = [{"id": 1, "cost": "500", "rate": "4.0", "cuisines": "A", "extra": "yes"}]
        out = run_pipeline(raw, column_map=COL)
        assert out[0]["id"] == 1
        assert out[0]["extra"] == "yes"
        assert out[0]["price"] == 500
        assert out[0]["rating"] == 4.0
        assert out[0]["cuisines"] == ["A"]

    def test_empty_input(self):
        assert run_pipeline([], column_map=COL) == []

    def test_optional_price_missing(self):
        raw = [{"rate": "4.0", "cuisines": "Cafe"}]  # no cost key
        out = run_pipeline(raw, column_map=COL)
        assert len(out) == 1
        assert out[0]["rating"] == 4.0
        assert out[0]["price"] is None
        assert out[0]["cuisines"] == ["Cafe"]

    def test_required_columns_configurable(self):
        raw = [{"cost": "500", "rate": "4.0", "cuisines": "Cafe"}]
        out = run_pipeline(raw, column_map=COL, required_columns=[])
        assert len(out) == 1
        out2 = run_pipeline(raw, column_map=COL, required_columns=["rating"])
        assert len(out2) == 1


class TestSaveCleaned:
    def test_save_csv(self):
        clean = [
            {"name": "R1", "price": 500, "rating": 4.0, "cuisines": ["A", "B"]},
        ]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "out.csv"
            save_cleaned(clean, path, format="csv")
            assert path.exists()
            with open(path, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == 1
            assert rows[0]["name"] == "R1"
            assert rows[0]["price"] == "500"
            assert rows[0]["rating"] == "4.0"
            # list serialized as comma-joined
            assert rows[0]["cuisines"] == "A,B"

    def test_save_csv_empty(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "empty.csv"
            save_cleaned([], path, format="csv")
            assert path.read_text() == ""

    def test_default_column_map_keys(self):
        assert "price" in DEFAULT_COLUMN_MAP
        assert "rating" in DEFAULT_COLUMN_MAP
        assert "cuisines" in DEFAULT_COLUMN_MAP
