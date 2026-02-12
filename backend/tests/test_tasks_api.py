"""
Tests for the tasks API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


class TestTasksEndpoints:

    def test_pending_tasks_requires_auth(self, client):
        response = client.get("/api/tasks/pending")
        assert response.status_code == 401

    def test_approve_task_requires_auth(self, client):
        response = client.post("/api/tasks/task_123/approve", json={"approved": True})
        assert response.status_code == 401
