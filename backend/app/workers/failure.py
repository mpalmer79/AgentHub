from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FailureInfo:
    code: str
    retryable: bool
    message: str


def classify_failure(exc: Exception) -> FailureInfo:
    """
    Map raw exceptions to stable failure codes.

    Keep this taxonomy small and explicit. You can grow it, but avoid churn:
    codes become contracts that power dashboards, alerts, and routing.
    """
    msg = str(exc) or exc.__class__.__name__
    low = msg.lower()

    # Configuration / missing env
    if "not configured" in low or "missing" in low and ("key" in low or "token" in low):
        return FailureInfo(code="CONFIG_MISSING", retryable=False, message=msg)

    # Auth / OAuth / integration problems
    if "invalid_grant" in low or "token" in low and ("expired" in low or "invalid" in low):
        return FailureInfo(code="AUTH_REQUIRED", retryable=False, message=msg)
    if "401" in low or "403" in low or "unauthorized" in low or "forbidden" in low:
        return FailureInfo(code="AUTH_REQUIRED", retryable=False, message=msg)

    # Rate limits
    if "429" in low or "rate limit" in low or "too many requests" in low:
        return FailureInfo(code="RATE_LIMITED", retryable=True, message=msg)

    # Provider 5xx
    if "500" in low or "502" in low or "503" in low or "504" in low or "server error" in low:
        return FailureInfo(code="PROVIDER_ERROR", retryable=True, message=msg)

    # Model/provider-specific errors
    if "anthropic" in low or "openai" in low or "model" in low and "error" in low:
        return FailureInfo(code="MODEL_ERROR", retryable=True, message=msg)

    # Explicit cancellation (if your runtime throws one later, wire it here)
    if "cancel" in low:
        return FailureInfo(code="TASK_CANCELLED", retryable=False, message=msg)

    # Tool-level issues
    if "tool" in low:
        return FailureInfo(code="TOOL_ERROR", retryable=False, message=msg)

    return FailureInfo(code="UNKNOWN", retryable=False, message=msg)
