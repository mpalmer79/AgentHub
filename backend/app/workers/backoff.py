from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_backoff_seconds(attempt: int) -> int:
    """
    attempt is 1-based (first failure => attempt=1).
    """
    if attempt <= 1:
        return 15
    if attempt == 2:
        return 60
    return 300  # 5 minutes


def compute_next_run_at(attempt: int) -> str:
    dt = utc_now() + timedelta(seconds=compute_backoff_seconds(attempt))
    return dt.isoformat()
