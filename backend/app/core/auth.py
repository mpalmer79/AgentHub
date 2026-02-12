from dataclasses import dataclass
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header

import time
import httpx
from jose import jwt, jwk
from jose.utils import base64url_decode

from app.core.config import settings


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: Optional[str]
    role: Optional[str]
    token: str


class JWKSCache:
    def __init__(self, jwks_url: str, ttl_seconds: int = 600):
        self.jwks_url = jwks_url
        self.ttl_seconds = ttl_seconds
        self._cached_at = 0.0
        self._keys: Dict[str, Dict[str, Any]] = {}

    def _expired(self) -> bool:
        return (time.time() - self._cached_at) > self.ttl_seconds

    def get_key(self, kid: str) -> Optional[Dict[str, Any]]:
        if not self.jwks_url:
            return None
        if not self._keys or self._expired():
            self.refresh()
        return self._keys.get(kid)

    def refresh(self) -> None:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(self.jwks_url)
            resp.raise_for_status()
            payload = resp.json()

        keys = payload.get("keys", [])
        mapped: Dict[str, Dict[str, Any]] = {}
        for k in keys:
            if "kid" in k:
                mapped[k["kid"]] = k

        self._keys = mapped
        self._cached_at = time.time()


_jwks_cache = JWKSCache(settings.resolved_jwks_url())


def _get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty bearer token")
    return token


def _verify_jwt(token: str) -> Dict[str, Any]:
    try:
        headers = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid JWT header")

    kid = headers.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="JWT missing kid")

    jwk_dict = _jwks_cache.get_key(kid)
    if not jwk_dict:
        raise HTTPException(status_code=401, detail="Unknown signing key")

    issuer = settings.resolved_issuer()
    audience = settings.SUPABASE_JWT_AUDIENCE

    try:
        # jose.jwt.decode will validate signature, exp, nbf, iss, aud
        payload = jwt.decode(
            token,
            jwk_dict,
            algorithms=[headers.get("alg", "RS256")],
            audience=audience,
            issuer=issuer,
            options={
                "verify_aud": True,
                "verify_iss": True,
            },
        )
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    token = _get_bearer_token(authorization)
    payload = _verify_jwt(token)

    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: no user id")

    return CurrentUser(id=user_id, email=email, role=role, token=token)
