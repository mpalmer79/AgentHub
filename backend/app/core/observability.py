"""Optional Sentry integration.

No-op when SENTRY_DSN is unset, so local and CI runs stay clean.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


def init_sentry() -> bool:
    """Initialize Sentry if a DSN is configured. Returns True on success."""
    dsn = settings.SENTRY_DSN
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        log.warning("sentry_disabled_missing_dep")
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.ENVIRONMENT,
        release=settings.VERSION,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[StarletteIntegration(), FastApiIntegration()],
        send_default_pii=False,
    )
    log.info("sentry_initialized", extra={"environment": settings.ENVIRONMENT})
    return True
