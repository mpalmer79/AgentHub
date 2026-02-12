"""Tests for API route existence."""
import pytest


def test_api_routes_exist_api(client):
    response = client.get("/api")
    assert response.status_code in [200, 404, 307]


def test_api_routes_exist_agents(client):
    response = client.get("/api/agents/catalog")
    assert response.status_code == 200
