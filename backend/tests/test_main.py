"""Tests for FastAPI app, including health and readiness probes."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_responds(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == settings.PROJECT_NAME
    assert body["status"] == "operational"


def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["version"] == settings.VERSION


def test_readiness_endpoint_reports_dependency_status(client):
    # CI env sets the placeholder secrets, so readiness should pass.
    response = client.get("/health/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "checks" in body
    assert "supabase_config" in body["checks"]
    assert "anthropic" in body["checks"]
    assert "encryption" in body["checks"]


def test_readiness_fails_when_critical_config_missing(monkeypatch, client):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    response = client.get("/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["anthropic"]["healthy"] is False
