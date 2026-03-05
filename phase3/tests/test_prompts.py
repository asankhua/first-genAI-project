"""
Unit tests for prompt building (Phase 3.2). No API key required.
"""

from src.prompts import build_recommendation_prompt, system_prompt


def test_build_prompt_includes_criteria():
    candidates = [
        {"name": "R1", "rating": 4.5, "price": 500, "cuisines": ["North Indian"]},
    ]
    p = build_recommendation_prompt(
        place="Bangalore",
        min_rating=4.0,
        max_price=1000,
        cuisine="North Indian",
        candidates=candidates,
        top_n=3,
    )
    assert "Bangalore" in p
    assert "4.0" in p
    assert "1000" in p
    assert "North Indian" in p
    assert "R1" in p
    assert "top 3" in p.lower() or "3 options" in p.lower()


def test_system_prompt_non_empty():
    s = system_prompt()
    assert len(s) > 0
    assert "restaurant" in s.lower()
