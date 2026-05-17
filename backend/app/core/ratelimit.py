"""Per-IP rate limiting via slowapi.

Lazy-imported so the import failure surfaces only if rate limiting is
actually wired in (helpful for unit tests that skip middleware).
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def _client_key(request) -> str:
    """Prefer the real client when behind a proxy; fall back to peer IP."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(
    key_func=_client_key,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    headers_enabled=True,
)
