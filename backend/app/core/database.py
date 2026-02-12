from typing import Optional
from supabase import create_client, Client

from app.core.config import settings


def _create_client(key: str) -> Client:
    if not settings.SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL is not configured")
    return create_client(settings.SUPABASE_URL, key)


def get_supabase_admin() -> Client:
    """
    Service-role client.
    Bypasses RLS.
    Use ONLY in trusted server-side contexts (workers, webhooks).
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not configured")

    return _create_client(settings.SUPABASE_SERVICE_ROLE_KEY)


def get_supabase_user(user_jwt: str) -> Client:
    """
    User-scoped client.
    Enforces RLS using the user's JWT.
    """
    if not settings.SUPABASE_ANON_KEY:
        raise RuntimeError("SUPABASE_ANON_KEY is not configured")

    client = _create_client(settings.SUPABASE_ANON_KEY)
    client.auth.set_session(user_jwt, "")
    return client


def get_supabase(user_jwt: Optional[str] = None) -> Client:
    """
    Unified accessor.

    - If JWT provided → user-scoped client
    - Otherwise → admin client
    """
    if user_jwt:
        return get_supabase_user(user_jwt)

    return get_supabase_admin()
