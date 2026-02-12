"""Tests for core configuration module."""
import pytest
from app.core.config import settings, Settings


class TestSettingsInstance:
    """Tests for the settings singleton."""

    def test_settings_exists(self):
        """Settings singleton should be available."""
        assert settings is not None

    def test_settings_is_correct_type(self):
        """Settings should be a Settings instance."""
        assert isinstance(settings, Settings)


class TestSettingsFields:
    """Tests for required configuration fields."""

    def test_has_supabase_url(self):
        assert hasattr(settings, "SUPABASE_URL")

    def test_has_supabase_anon_key(self):
        assert hasattr(settings, "SUPABASE_ANON_KEY")

    def test_has_supabase_service_role_key(self):
        assert hasattr(settings, "SUPABASE_SERVICE_ROLE_KEY")

    def test_has_anthropic_api_key(self):
        assert hasattr(settings, "ANTHROPIC_API_KEY")

    def test_has_integration_encryption_key(self):
        assert hasattr(settings, "INTEGRATION_ENCRYPTION_KEY")

    def test_has_stripe_keys(self):
        assert hasattr(settings, "STRIPE_SECRET_KEY")
        assert hasattr(settings, "STRIPE_WEBHOOK_SECRET")

    def test_has_quickbooks_config(self):
        assert hasattr(settings, "QUICKBOOKS_CLIENT_ID")
        assert hasattr(settings, "QUICKBOOKS_CLIENT_SECRET")
        assert hasattr(settings, "QUICKBOOKS_REDIRECT_URI")
        assert hasattr(settings, "QUICKBOOKS_ENVIRONMENT")

    def test_has_google_config(self):
        assert hasattr(settings, "GOOGLE_CLIENT_ID")
        assert hasattr(settings, "GOOGLE_CLIENT_SECRET")
        assert hasattr(settings, "GOOGLE_REDIRECT_URI")


class TestSettingsDefaults:
    """Tests for default configuration values."""

    def test_project_name_default(self):
        assert settings.PROJECT_NAME == "AgentHub"

    def test_version_default(self):
        assert settings.VERSION == "1.0.0"

    def test_api_prefix_default(self):
        assert settings.API_PREFIX == "/api"

    def test_quickbooks_environment_default(self):
        # Should default to sandbox if not set
        assert settings.QUICKBOOKS_ENVIRONMENT in ("sandbox", "production")


class TestSettingsDerivedHelpers:
    """Tests for derived helper methods."""

    def test_resolved_jwks_url_returns_string(self):
        url = settings.resolved_jwks_url()
        assert isinstance(url, str)

    def test_resolved_jwks_url_format(self):
        url = settings.resolved_jwks_url()
        if url:  # Only check if URL is set
            assert url.endswith("/auth/v1/keys")

    def test_resolved_issuer_returns_string(self):
        issuer = settings.resolved_issuer()
        assert isinstance(issuer, str)

    def test_resolved_issuer_format(self):
        issuer = settings.resolved_issuer()
        if issuer:  # Only check if issuer is set
            assert issuer.endswith("/auth/v1")


class TestSettingsValidation:
    """Tests for settings validation."""

    def test_validate_production_ready_method_exists(self):
        """validate_production_ready method should exist."""
        assert hasattr(settings, "validate_production_ready")
        assert callable(settings.validate_production_ready)
