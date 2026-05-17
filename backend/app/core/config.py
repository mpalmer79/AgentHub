from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Core App
    PROJECT_NAME: str = "AgentHub"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development|staging|production

    # Observability
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

    # Rate limiting (slowapi syntax: "N/period")
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
    RATE_LIMIT_AUTH: str = os.getenv("RATE_LIMIT_AUTH", "10/minute")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").rstrip("/")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # Supabase JWT Verification
    SUPABASE_JWKS_URL: str = os.getenv("SUPABASE_JWKS_URL", "")
    SUPABASE_JWT_AUDIENCE: str = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")
    SUPABASE_JWT_ISSUER: str = os.getenv("SUPABASE_JWT_ISSUER", "")

    # Encryption (OAuth token protection)
    INTEGRATION_ENCRYPTION_KEY: str = os.getenv("INTEGRATION_ENCRYPTION_KEY", "")

    # AI Providers
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Agent runtime
    AGENT_MODEL: str = os.getenv("AGENT_MODEL", "claude-sonnet-4-20250514")
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    AGENT_MAX_OUTPUT_TOKENS: int = int(os.getenv("AGENT_MAX_OUTPUT_TOKENS", "4096"))
    # Hard ceiling on cumulative input+output tokens per single task. 0 disables.
    AGENT_MAX_TOKENS_PER_TASK: int = int(os.getenv("AGENT_MAX_TOKENS_PER_TASK", "200000"))

    # QuickBooks
    QUICKBOOKS_CLIENT_ID: str = os.getenv("QUICKBOOKS_CLIENT_ID", "")
    QUICKBOOKS_CLIENT_SECRET: str = os.getenv("QUICKBOOKS_CLIENT_SECRET", "")
    QUICKBOOKS_REDIRECT_URI: str = os.getenv("QUICKBOOKS_REDIRECT_URI", "")
    QUICKBOOKS_ENVIRONMENT: str = os.getenv("QUICKBOOKS_ENVIRONMENT", "sandbox")
    QUICKBOOKS_WEBHOOK_VERIFIER_TOKEN: str = os.getenv("QUICKBOOKS_WEBHOOK_VERIFIER_TOKEN", "")

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
        "http://localhost:3000,http://localhost:5173,https://agent-hub-amber.vercel.app",
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

    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    # ---------- Validation ----------

    def validate_production_ready(self) -> None:
        """Raise if any production-critical secret is missing.

        Called from `lifespan` when ENVIRONMENT=production so a misconfigured
        deploy fails fast instead of serving 500s.
        """
        missing = []
        required = [
            ("SUPABASE_URL", self.SUPABASE_URL),
            ("SUPABASE_ANON_KEY", self.SUPABASE_ANON_KEY),
            ("SUPABASE_SERVICE_ROLE_KEY", self.SUPABASE_SERVICE_ROLE_KEY),
            ("INTEGRATION_ENCRYPTION_KEY", self.INTEGRATION_ENCRYPTION_KEY),
            ("ANTHROPIC_API_KEY", self.ANTHROPIC_API_KEY),
        ]
        for name, value in required:
            if not value:
                missing.append(name)
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


settings = Settings()
