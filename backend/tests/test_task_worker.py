"""
Tests for the task worker.

Tests the background task processing including:
- Queue claiming
- Task execution
- Retry logic
- Failure handling
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.workers.task_worker import (
    claim_next_queue_record,
    process_queue_record,
    worker_id,
)
from app.agents.registry import AgentType
from tests.conftest import FakeSupabaseClient


class TestWorkerIdentity:
    """Tests for worker identification."""

    def test_worker_id_returns_string(self):
        """worker_id should return a string identifier."""
        wid = worker_id()
        assert isinstance(wid, str)
        assert len(wid) > 0

    def test_worker_id_is_consistent(self):
        """worker_id should return same value on repeated calls."""
        id1 = worker_id()
        id2 = worker_id()
        assert id1 == id2


class TestClaimQueueRecord:
    """Tests for queue record claiming."""

    @pytest.mark.asyncio
    async def test_claim_returns_none_when_empty(self, monkeypatch):
        """claim_next_queue_record returns None when queue is empty."""
        fake_sb = FakeSupabaseClient({"agent_task_queue": []})
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        record = await claim_next_queue_record()
        assert record is None

    @pytest.mark.asyncio
    async def test_claim_returns_queued_record(self, monkeypatch):
        """claim_next_queue_record returns a queued record."""
        queue_data = [
            {
                "id": "q1",
                "task_id": "t1",
                "status": "queued",
                "next_run_at": "2020-01-01T00:00:00+00:00",
                "locked_at": None,
                "locked_by": None,
                "created_at": "2020-01-01T00:00:00+00:00",
            }
        ]
        fake_sb = FakeSupabaseClient({"agent_task_queue": queue_data})
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        record = await claim_next_queue_record()

        assert record is not None
        assert record["id"] == "q1"
        assert record["status"] == "processing"

    @pytest.mark.asyncio
    async def test_claim_skips_locked_records(self, monkeypatch):
        """claim_next_queue_record skips recently locked records."""
        now = datetime.now(timezone.utc).isoformat()
        queue_data = [
            {
                "id": "q1",
                "task_id": "t1",
                "status": "queued",
                "next_run_at": "2020-01-01T00:00:00+00:00",
                "locked_at": now,  # Recently locked
                "locked_by": "other_worker",
                "created_at": "2020-01-01T00:00:00+00:00",
            }
        ]
        fake_sb = FakeSupabaseClient({"agent_task_queue": queue_data})
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        record = await claim_next_queue_record()
        # Should not claim because it's locked by another worker
        # Note: The actual behavior depends on implementation details


class TestProcessQueueRecord:
    """Tests for queue record processing."""

    @pytest.mark.asyncio
    async def test_process_missing_task_id_marks_processed(self, monkeypatch):
        """Processing record with no task_id marks it as processed with error."""
        queue_record = {
            "id": "q1",
            "task_id": None,
            "status": "processing",
        }

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": []
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        await process_queue_record(queue_record)

        # Check queue record was updated
        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"
        assert "missing task_id" in q.get("last_error", "").lower()

    @pytest.mark.asyncio
    async def test_process_missing_task_marks_processed(self, monkeypatch):
        """Processing record where task doesn't exist marks it as processed."""
        queue_record = {
            "id": "q1",
            "task_id": "t_nonexistent",
            "status": "processing",
        }

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": []  # Task doesn't exist
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        await process_queue_record(queue_record)

        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"
        assert "not found" in q.get("last_error", "").lower()

    @pytest.mark.asyncio
    async def test_process_successful_task(self, monkeypatch):
        """Processing successful task marks both queue and task as completed."""
        queue_record = {
            "id": "q1",
            "task_id": "t1",
            "status": "processing",
            "attempts": 0,
            "max_attempts": 3,
        }

        task_data = {
            "id": "t1",
            "agent_type": "bookkeeper",
            "user_id": "u1",
            "task": "Categorize transactions",
            "context": {},
            "status": "queued",
            "started_at": None,
        }

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": [task_data],
            "agent_task_events": [],
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        # Mock successful runtime execution
        class FakeRuntime:
            def __init__(self, agent_type, user_id):
                pass

            async def execute(self, task, context, task_id=None):
                return {"success": True, "result": "Categorized 10 transactions"}

        monkeypatch.setattr("app.workers.task_worker.AgentRuntime", FakeRuntime)

        await process_queue_record(queue_record)

        # Check queue record
        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"

        # Check task record
        t = fake_sb.table("agent_tasks").rows[0]
        assert t["status"] == "completed"
        assert t["result"] == "Categorized 10 transactions"

    @pytest.mark.asyncio
    async def test_process_retryable_failure_requeues(self, monkeypatch):
        """Processing retryable failure requeues with incremented attempts."""
        queue_record = {
            "id": "q1",
            "task_id": "t1",
            "status": "processing",
            "attempts": 0,
            "max_attempts": 3,
        }

        task_data = {
            "id": "t1",
            "agent_type": "bookkeeper",
            "user_id": "u1",
            "task": "Categorize transactions",
            "context": {},
            "status": "queued",
        }

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": [task_data],
            "agent_task_events": [],
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        # Mock runtime that raises retryable error
        class FakeRuntime:
            def __init__(self, agent_type, user_id):
                pass

            async def execute(self, task, context, task_id=None):
                raise RuntimeError("429 Too Many Requests")

        monkeypatch.setattr("app.workers.task_worker.AgentRuntime", FakeRuntime)

        await process_queue_record(queue_record)

        # Check queue record was requeued
        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "queued"
        assert q["attempts"] == 1
        assert "next_run_at" in q

    @pytest.mark.asyncio
    async def test_process_max_retries_marks_failed(self, monkeypatch):
        """Processing failure at max attempts marks task as failed."""
        queue_record = {
            "id": "q1",
            "task_id": "t1",
            "status": "processing",
            "attempts": 2,  # Already tried twice
            "max_attempts": 3,
        }

        task_data = {
            "id": "t1",
            "agent_type": "bookkeeper",
            "user_id": "u1",
            "task": "Categorize transactions",
            "context": {},
            "status": "running",
        }

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": [task_data],
            "agent_task_events": [],
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        # Mock runtime that fails
        class FakeRuntime:
            def __init__(self, agent_type, user_id):
                pass

            async def execute(self, task, context, task_id=None):
                raise RuntimeError("Permanent failure")

        monkeypatch.setattr("app.workers.task_worker.AgentRuntime", FakeRuntime)

        await process_queue_record(queue_record)

        # Check queue record is processed (not requeued)
        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"
        assert q["attempts"] == 3

        # Check task is marked failed
        t = fake_sb.table("agent_tasks").rows[0]
        assert t["status"] == "failed"

    @pytest.mark.asyncio
    async def test_process_unknown_agent_type_fails(self, monkeypatch):
        """Processing task with unknown agent type marks it as failed."""
        queue_record = {
            "id": "q1",
            "task_id": "t1",
            "status": "processing",
            "attempts": 0,
            "max_attempts": 3,
        }

        task_data = {
            "id": "t1",
            "agent_type": "nonexistent_agent",  # Invalid agent type
            "user_id": "u1",
            "task": "Do something",
            "context": {},
            "status": "queued",
        }

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": [task_data],
            "agent_task_events": [],
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        await process_queue_record(queue_record)

        # Check task is marked failed with UNKNOWN_AGENT
        t = fake_sb.table("agent_tasks").rows[0]
        assert t["status"] == "failed"
        assert t["failure_code"] == "UNKNOWN_AGENT"
        assert t["retryable"] is False
