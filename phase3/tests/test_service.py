"""
Tests for recommendation service. Groq API is mocked so no API key needed for unit tests.
Integration test (real Groq call) is skipped unless GROQ_API_KEY is set.
"""

import os
from unittest.mock import patch

import pytest
from src.service import get_recommendations, _parse_recommendations


def test_get_recommendations_returns_empty_when_no_candidates():
    result = get_recommendations(
        cleaned_rows=[],
        place="Nowhere",
        rating=4.0,
    )
    assert result["candidates_count"] == 0
    assert result["recommendations"] == []
    assert "No matching" in result["raw_response"]


def test_get_recommendations_returns_empty_when_filter_matches_nothing():
    rows = [{"location": "Mumbai", "rating": 4.0, "price": 500, "cuisines": []}]
    result = get_recommendations(rows, place="Bangalore", rating=4.0)
    assert result["candidates_count"] == 0
    assert result["recommendations"] == []


@patch("src.service.get_completion")
def test_get_recommendations_parses_llm_response(mock_completion):
    mock_completion.return_value = (
        "- Restaurant A: Great rating and value.\n"
        "- Restaurant B: Fits your cuisine preference.\n"
    )
    rows = [
        {"location": "City", "name": "R1", "rating": 4.5, "price": 500, "cuisines": ["North Indian"]},
    ]
    result = get_recommendations(rows, place="City", rating=4.0)
    assert result["candidates_count"] == 1
    assert mock_completion.called
    assert len(result["recommendations"]) >= 1
    assert any("Restaurant A" in r.get("name", "") or "Great" in r.get("reason", "") for r in result["recommendations"])


def test_parse_recommendations():
    text = "- Cafe A: Good for breakfast.\n- Cafe B: Nice ambiance."
    out = _parse_recommendations(text)
    assert len(out) == 2
    assert out[0]["name"] == "Cafe A"
    assert out[0]["reason"] == "Good for breakfast."
    assert out[1]["name"] == "Cafe B"
    assert out[1]["reason"] == "Nice ambiance."


def test_parse_recommendations_numbered():
    text = "1. Place One: Reason one.\n2. Place Two: Reason two."
    out = _parse_recommendations(text)
    assert len(out) == 2
    assert "Place One" in out[0]["name"]
    assert "Reason one" in out[0]["reason"]


def test_parse_recommendations_fallback():
    text = "Just a paragraph with no bullets."
    out = _parse_recommendations(text)
    assert len(out) == 1
    assert out[0]["name"] == "Recommendation"
    assert "paragraph" in out[0]["reason"]


@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set; run integration test after connecting API key",
)
def test_get_recommendations_integration_real_groq():
    """Integration test: real Groq call. Run only when GROQ_API_KEY is set."""
    rows = [
        {"location": "Bangalore", "name": "Test Restaurant", "rating": 4.5, "price": 600, "cuisines": ["North Indian"]},
    ]
    result = get_recommendations(rows, place="Bangalore", rating=4.0, top_n=2)
    assert result["candidates_count"] == 1
    assert "raw_response" in result
    assert isinstance(result["recommendations"], list)
