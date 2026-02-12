from __future__ import annotations

import asyncio
import os
import socket
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from app.core.database import get_supabase_admin
from app.agents.registry import AgentType
from app.agents.runtime import AgentRuntime
from app.workers.failure import classify_failure
from app.workers.backoff import compute_next_run_at, utc_now


LOCK_STALE_AFTER = timedelta(minutes=10)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def worker_id() -> str:
    # Stable-ish identity for locks
    return os.getenv("WORKER_ID") or f"{socket.gethostname()}:{os.getpid()}"


def _lock_is_stale(locked_at_iso: Optional[str]) -> bool:
    if not locked_at_iso:
        return False
    try:
        locked_at = datetime.fromisoformat(locked_at_iso.replace("Z", "+00:00"))
        return utc_now() - locked_at > LOCK_STALE_AFTER
    except Exception:
        return True


async def claim_next_queue_record() -> Optional[Dict[str, Any]]:
    """
    Best-effort claiming using a select-then-conditional-update pattern.

    Not perfectly atomic, but the conditional update prevents most duplicates.
    If you later add RPC support, we can convert this to an atomic claim function.
    """
    sb = get_supabase_admin()

    # 1) Find candidates that are ready to run
    res = (
        sb.table("agent_task_queue")
        .select("*")
        .eq("status", "queued")
        .lte("next_run_at", utc_now_iso())
        .order("created_at")
        .limit(5)
        .execute()
    )
    rows = res.data or []
    if not rows:
        return None

    wid = worker_id()

    # 2) Try to claim one
    for row in rows:
        qid = row.get("id")
        if not qid:
            continue

        locked_at = row.get("locked_at")
        # allow reclaim if lock is stale
        allow_reclaim = (locked_at is None) or _lock_is_stale(locked_at)
        if not allow_reclaim:
            continue

        # Conditional update: only claim if still queued AND (unlocked OR stale)
        update = {
            "status": "processing",
            "locked_at": utc_now_iso(),
            "locked_by": wid,
        }

        # If stale lock, clear it first by overwriting in same update (already done)
        upd = (
            sb.table("agent_task_queue")
            .update(update)
            .eq("id", qid)
            .eq("status", "queued")
            .execute()
        )

        # Our minimal client may not return affected row count;
        # so re-read and confirm we own it.
        confirm = (
            sb.table("agent_task_queue")
            .select("*")
            .eq("id", qid)
            .single()
            .execute()
        )
        claimed = confirm.data or {}
        if claimed.get("status") == "processing" and claimed.get("locked_by") == wid:
            return claimed

    return None


async def process_queue_record(queue_record: Dict[str, Any]) -> None:
    sb = get_supabase_admin()

    qid = queue_record["id"]
    tid = queue_record.get("task_id")
    if not tid:
        sb.table("agent_task_queue").update(
            {"status": "processed", "processed_at": utc_now_iso(), "last_error": "Queue record missing task_id"}
        ).eq("id", qid).execute()
        return

    # Load task
    task_res = sb.table("agent_tasks").select("*").eq("id", tid).single().execute()
    task = task_res.data or {}
    if not task:
        sb.table("agent_task_queue").update(
            {"status": "processed", "processed_at": utc_now_iso(), "last_error": f"Task {tid} not found"}
        ).eq("id", qid).execute()
        return

    # Mark task started if not already
    if not task.get("started_at"):
        sb.table("agent_tasks").update({"status": "running", "started_at": utc_now_iso()}).eq("id", tid).execute()

    agent_type_str = task.get("agent_type")
    user_id = task.get("user_id")
    task_text = task.get("task")
    context = task.get("context") or {}

    # Validate agent type
    try:
        agent_type = AgentType(agent_type_str)
    except Exception as exc:
        fi = classify_failure(exc)
        sb.table("agent_tasks").update({
            "status": "failed",
            "failure_code": "UNKNOWN_AGENT",
            "retryable": False,
            "error_detail": f"Unknown agent type: {agent_type_str}",
            "completed_at": utc_now_iso(),
        }).eq("id", tid).execute()
        sb.table("agent_task_queue").update({"status": "processed", "processed_at": utc_now_iso()}).eq("id", qid).execute()
        return

    # Execute
    runtime = AgentRuntime(agent_type, user_id)
    try:
        result = await runtime.execute(task_text, context, task_id=tid)
        success = bool(result.get("success"))
        if success:
            # Complete task
            sb.table("agent_tasks").update({
                "status": "completed",
                "completed_at": utc_now_iso(),
                "result": result.get("result"),
                "failure_code": None,
                "retryable": False,
                "error_detail": None,
            }).eq("id", tid).execute()

            sb.table("agent_task_queue").update({
                "status": "processed",
                "processed_at": utc_now_iso(),
                "last_error": None,
                "locked_at": None,
                "locked_by": None,
            }).eq("id", qid).execute()
            return

        # Runtime returned failure
        err = result.get("error") or "Task failed"
        raise RuntimeError(err)

    except Exception as exc:
        fi = classify_failure(exc)

        # increment attempts
        attempts = int(queue_record.get("attempts") or 0) + 1
        max_attempts = int(queue_record.get("max_attempts") or 3)

        # persist task classification (task is business-level record)
        sb.table("agent_tasks").update({
            "failure_code": fi.code,
            "retryable": fi.retryable,
            "error_detail": fi.message,
        }).eq("id", tid).execute()

        if fi.retryable and attempts < max_attempts:
            next_run_at = compute_next_run_at(attempts)
            # Put back into queue for retry
            sb.table("agent_task_queue").update({
                "status": "queued",
                "attempts": attempts,
                "next_run_at": next_run_at,
                "last_error": fi.message,
                "locked_at": None,
                "locked_by": None,
            }).eq("id", qid).execute()
            return

        # Final failure
        sb.table("agent_tasks").update({
            "status": "failed",
            "completed_at": utc_now_iso(),
        }).eq("id", tid).execute()

        sb.table("agent_task_queue").update({
            "status": "processed",
            "processed_at": utc_now_iso(),
            "attempts": attempts,
            "last_error": fi.message,
            "locked_at": None,
            "locked_by": None,
        }).eq("id", qid).execute()
        return


async def worker_loop(poll_interval: float = 2.0) -> None:
    while True:
        try:
            record = await claim_next_queue_record()
            if not record:
                await asyncio.sleep(poll_interval)
                continue

            await process_queue_record(record)
        except Exception:
            # Don't crash the worker; avoid tight-looping
            await asyncio.sleep(poll_interval)


def main() -> None:
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
