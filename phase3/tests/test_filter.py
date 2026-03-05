"""
Unit tests for filtering layer (Phase 3.1). No API key required.
"""

import pytest
from src.filter import filter_by_criteria


def test_filter_by_place_and_rating():
    rows = [
        {"location": "Bangalore", "rating": 4.5, "price": 500, "cuisines": ["North Indian"]},
        {"location": "Mumbai", "rating": 4.0, "price": 800, "cuisines": ["Chinese"]},
        {"location": "Bangalore", "rating": 3.5, "price": 300, "cuisines": ["Cafe"]},
    ]
    out = filter_by_criteria(rows, place="Bangalore", min_rating=4.0)
    assert len(out) == 1
    assert out[0]["location"] == "Bangalore" and out[0]["rating"] == 4.5


def test_filter_by_place_case_insensitive():
    rows = [{"location": "New Delhi", "rating": 4.0, "price": 600, "cuisines": []}]
    out = filter_by_criteria(rows, place="delhi", min_rating=3.0)
    assert len(out) == 1


def test_filter_by_max_price():
    rows = [
        {"location": "City", "rating": 4.0, "price": 500, "cuisines": []},
        {"location": "City", "rating": 4.2, "price": 1500, "cuisines": []},
    ]
    out = filter_by_criteria(rows, place="City", min_rating=4.0, max_price=1000)
    assert len(out) == 1
    assert out[0]["price"] == 500


def test_filter_by_cuisine():
    rows = [
        {"location": "City", "rating": 4.0, "price": 500, "cuisines": ["North Indian", "Chinese"]},
        {"location": "City", "rating": 4.0, "price": 500, "cuisines": ["Bakery"]},
    ]
    out = filter_by_criteria(rows, place="City", min_rating=4.0, cuisine="North Indian")
    assert len(out) == 1
    assert "North Indian" in out[0]["cuisines"]


def test_empty_place_returns_empty():
    rows = [{"location": "City", "rating": 4.0, "price": 500, "cuisines": []}]
    out = filter_by_criteria(rows, place="", min_rating=4.0)
    assert out == []


def test_max_candidates_cap():
    rows = [
        {"location": "City", "rating": 4.0 + i * 0.1, "price": 500, "cuisines": []}
        for i in range(20)
    ]
    out = filter_by_criteria(rows, place="City", min_rating=4.0, max_candidates=5)
    assert len(out) == 5


def test_custom_place_column():
    rows = [{"city": "Pune", "rating": 4.0, "price": 400, "cuisines": []}]
    out = filter_by_criteria(rows, place="Pune", min_rating=3.0, place_column="city")
    assert len(out) == 1


def test_place_matches_listed_in_city():
    """Zomato: listed_in(city) groups areas; match place against both location and listed_in(city)."""
    rows = [
        {"location": "Basavanagudi", "listed_in(city)": "Banashankari", "rating": 4.0, "price": 400, "cuisines": []},
        {"location": "Banashankari", "listed_in(city)": "Banashankari", "rating": 4.2, "price": 300, "cuisines": []},
    ]
    out = filter_by_criteria(rows, place="Banashankari", min_rating=3.0)
    assert len(out) == 2
