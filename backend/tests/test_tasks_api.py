"""
Tests for the tasks API endpoints.

Tests the REST API including:
- Pending tasks retrieval
- Task approval/rejection
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import CurrentUser
from conftest import FakeSupabaseClient


class TestTasksEndpoints:
    """Tests for tasks API endpoints."""

    def test_pending_tasks_requires_auth(self, client):
        """Pending tasks endpoint requires authentication."""
        response = client.get("/api/tasks/pending")
        assert response.status_code == 401

    def test_approve_task_requires_auth(self, client):
        """Approve task endpoint requires authentication."""
        response = client.post(
            "/api/tasks/task_123/approve",
            json={"approved": True}
        )
        assert response.status_code == 401


class TestTaskApproval:
    """Tests for task approval logic."""

    @pytest.fixture
    def setup_task_approval(self, monkeypatch):
        """Setup mocked auth and Supabase for task approval tests."""
        fake_user = CurrentUser(
            id="user_123",
            email="test@example.com",
            role="authenticated",
            token="fake_jwt"
        )

        task_data = {
            "id": "task_123",
            "agent_type": "bookkeeper",
            "status": "awaiting_approval",
            "task": "Categorize transactions",
            "context": {},
            "created_at": "2026-01-01T00:00:00Z",
        }

        fake_sb = FakeSupabaseClient({
            "agent_tasks": [task_data],
            "agent_task_queue": []
        })

        monkeypatch.setattr(
            "app.core.database.get_supabase_user",
            lambda token: fake_sb
        )

        return fake_user, fake_sb, task_data
