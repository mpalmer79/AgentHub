"""Tests for main application."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_app_starts(client):
    response = client.get("/")
    assert response.status_code in [200, 404, 307]
