"""Tests for main application."""
import pytest


def test_app_starts(client):
    response = client.get("/")
    assert response.status_code in [200, 404, 307]
