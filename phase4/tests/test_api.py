"""
Tests for Phase 4 API. Recommendation service is mocked so no Phase 3 or Groq required.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@patch("src.app.get_recommendations")
def test_post_recommendations_success(mock_get, client: TestClient):
    mock_get.return_value = {
        "recommendations": [
            {"name": "Restaurant A", "reason": "Great rating and value."},
            {"name": "Restaurant B", "reason": "Fits your cuisine preference."},
        ],
        "raw_response": "Full LLM response here.",
        "candidates_count": 10,
    }
    r = client.post(
        "/recommendations",
        json={"place": "Bangalore", "rating": 4.0, "price": 1000, "cuisine": "North Indian"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["name"] == "Restaurant A"
    assert data["recommendations"][0]["reason"] == "Great rating and value."
    assert data["candidates_count"] == 10
    assert data["raw_response"] == "Full LLM response here."
    mock_get.assert_called_once()
    call_kw = mock_get.call_args[1]
    assert call_kw["place"] == "Bangalore"
    assert call_kw["rating"] == 4.0
    assert call_kw["price"] == 1000
    assert call_kw["cuisine"] == "North Indian"


@patch("src.app.get_recommendations")
def test_post_recommendations_optional_fields(mock_get, client: TestClient):
    mock_get.return_value = {"recommendations": [], "raw_response": "No matches.", "candidates_count": 0}
    r = client.post("/recommendations", json={"place": "Mumbai", "rating": 3.5})
    assert r.status_code == 200
    assert r.json()["candidates_count"] == 0
    call_kw = mock_get.call_args[1]
    assert call_kw["place"] == "Mumbai"
    assert call_kw["rating"] == 3.5
    assert call_kw["price"] is None
    assert call_kw["cuisine"] is None


def test_post_recommendations_validation_missing_place(client: TestClient):
    r = client.post("/recommendations", json={"rating": 4.0})
    assert r.status_code == 422  # Unprocessable Entity (validation)


def test_post_recommendations_validation_invalid_rating(client: TestClient):
    r = client.post("/recommendations", json={"place": "Delhi", "rating": 6.0})
    assert r.status_code == 422


def test_post_recommendations_validation_empty_place(client: TestClient):
    r = client.post("/recommendations", json={"place": "", "rating": 4.0})
    assert r.status_code == 422


@patch("src.app.get_recommendations")
def test_get_recommendations_success(mock_get, client: TestClient):
    mock_get.return_value = {
        "recommendations": [{"name": "Cafe X", "reason": "Good for breakfast."}],
        "raw_response": "OK",
        "candidates_count": 1,
    }
    r = client.get("/recommendations?place=Pune&rating=4.0")
    assert r.status_code == 200
    assert r.json()["recommendations"][0]["name"] == "Cafe X"


def test_get_recommendations_validation_missing_place(client: TestClient):
    r = client.get("/recommendations?rating=4.0")
    # FastAPI may return 422 for missing required query param
    assert r.status_code in (400, 422)


def test_get_recommendations_validation_invalid_rating(client: TestClient):
    r = client.get("/recommendations?place=City&rating=-1")
    assert r.status_code == 400


def test_get_locations(client: TestClient):
    r = client.get("/locations")
    assert r.status_code == 200
    data = r.json()
    assert "locations" in data
    assert isinstance(data["locations"], list)


def test_get_cuisines(client: TestClient):
    r = client.get("/cuisines")
    assert r.status_code == 200
    data = r.json()
    assert "cuisines" in data
    assert isinstance(data["cuisines"], list)
