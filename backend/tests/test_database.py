"""
Tests for database client utilities.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestDatabaseClients:
    """Tests for Supabase client factories."""

    def test_get_supabase_admin_callable(self):
        """get_supabase_admin should be callable."""
        from app.core.database import get_supabase_admin
        assert callable(get_supabase_admin)

    def test_get_supabase_user_callable(self):
        """get_supabase_user should be callable."""
        from app.core.database import get_supabase_user
        assert callable(get_supabase_user)

    def test_get_supabase_callable(self):
        """get_supabase should be callable."""
        from app.core.database import get_supabase
        assert callable(get_supabase)


class TestDatabaseClientBehavior:
    """Tests for client behavior."""

    def test_get_supabase_with_token_returns_user_client(self, monkeypatch):
        """get_supabase with token should return user-scoped client."""
        mock_user_client = MagicMock()
        mock_admin_client = MagicMock()

        monkeypatch.setattr(
            "app.core.database.get_supabase_user",
            lambda token: mock_user_client
        )
        monkeypatch.setattr(
            "app.core.database.get_supabase_admin",
            lambda: mock_admin_client
        )

        from app.core.database import get_supabase

        result = get_supabase("user_jwt_token")
        assert result == mock_user_client

    def test_get_supabase_without_token_returns_admin_client(self, monkeypatch):
        """get_supabase without token should return admin client."""
        mock_user_client = MagicMock()
        mock_admin_client = MagicMock()

        monkeypatch.setattr(
            "app.core.database.get_supabase_user",
            lambda token: mock_user_client
        )
        monkeypatch.setattr(
            "app.core.database.get_supabase_admin",
            lambda: mock_admin_client
        )

        from app.core.database import get_supabase

        result = get_supabase()
        assert result == mock_admin_client
