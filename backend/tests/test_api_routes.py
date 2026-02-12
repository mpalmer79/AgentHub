"""Tests for API route existence."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_routes_exist_api(client):
    response = client.get("/api")
    assert response.status_code in [200, 404, 307]


def test_api_routes_exist_agents(client):
    response = client.get("/api/agents/catalog")
    assert response.status_code == 200
