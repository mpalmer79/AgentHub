"""Verify auth endpoints are rate-limited."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.ratelimit import limiter
from app.main import app


@pytest.fixture
def client():
    # Each test gets a fresh limiter store so prior tests don't bleed in.
    limiter.reset()
    return TestClient(app)


def test_signin_rate_limit_kicks_in(client):
    # RATE_LIMIT_AUTH defaults to "10/minute". Send 11 requests; the 11th must 429.
    limit = int(settings.RATE_LIMIT_AUTH.split("/")[0])
    last_status = None
    for _ in range(limit + 1):
        resp = client.post("/api/auth/signin", json={
            "email": "user@example.com", "password": "wrong",
        })
        last_status = resp.status_code
    assert last_status == 429


def test_signup_rate_limit_kicks_in(client):
    limit = int(settings.RATE_LIMIT_AUTH.split("/")[0])
    last_status = None
    for _ in range(limit + 1):
        resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "abc12345",
            "full_name": "New User",
        })
        last_status = resp.status_code
    assert last_status == 429
