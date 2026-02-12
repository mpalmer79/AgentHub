from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Core App
    PROJECT_NAME: str = "AgentHub"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").rstrip("/")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # Supabase JWT Verification
    SUPABASE_JWKS_URL: str = os.getenv("SUPABASE_JWKS_URL", "")
    SUPABASE_JWT_AUDIENCE: str = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")
    SUPABASE_JWT_ISSUER: str = os.getenv("SUPABASE_JWT_ISSUER", "")

    # Encryption (OAuth token protection)
    INTEGRATION_ENCRYPTION_KEY: str = os.getenv("INTEGRATION_ENCRYPTION_KEY", "")

    # AI Providers
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # QuickBooks
    QUICKBOOKS_CLIENT_ID: str = os.getenv("QUICKBOOKS_CLIENT_ID", "")
    QUICKBOOKS_CLIENT_SECRET: str = os.getenv("QUICKBOOKS_CLIENT_SECRET", "")
    QUICKBOOKS_REDIRECT_URI: str = os.getenv("QUICKBOOKS_REDIRECT_URI", "")
    QUICKBOOKS_ENVIRONMENT: str = os.getenv("QUICKBOOKS_ENVIRONMENT", "sandbox")

    # Google
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    GOOGLE_CALENDAR_REDIRECT_URI: str = os.getenv("GOOGLE_CALENDAR_REDIRECT_URI", "")

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,https://agent-hub-amber.vercel.app"
    ).split(",")

    class Config:
        env_file = ".env"
        case_sensitive = True

    # ---------- Derived Helpers ----------

    def resolved_jwks_url(self) -> str:
        if self.SUPABASE_JWKS_URL:
            return self.SUPABASE_JWKS_URL
        if not self.SUPABASE_URL:
            return ""
        return f"{self.SUPABASE_URL}/auth/v1/keys"

    def resolved_issuer(self) -> str:
        if self.SUPABASE_JWT_ISSUER:
            return self.SUPABASE_JWT_ISSUER
        if not self.SUPABASE_URL:
            return ""
        return f"{self.SUPABASE_URL}/auth/v1"

    # ---------- Validation ----------

    def validate_production_ready(self) -> None:
        """
        Call this at startup in production to ensure
        critical secrets are configured.
        """
        missing = []

        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")

        if not self.SUPABASE_ANON_KEY:
            missing.append("SUPABASE_ANON_KEY")

        if not self.INTEGRATION_ENCRYPTION_KEY:
            missing.append("INTEGRATION_ENCRYPTION_KEY")

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


settings = Settings()
