"""
Tests for the task worker.
"""
import pytest
from datetime import datetime, timezone

from app.workers.task_worker import (
    claim_next_queue_record,
    process_queue_record,
    worker_id,
)
from app.agents.registry import AgentType


# === Fake Supabase (defined inline) ===

class FakeSupabaseResponse:
    def __init__(self, data=None):
        self.data = data


class FakeSupabaseQuery:
    def __init__(self, table, operation="select"):
        self._table = table
        self._operation = operation
        self._filters = {}
        self._payload = None
        self._single = False

    def select(self, *args): return self
    def insert(self, data):
        self._operation = "insert"
        self._payload = data
        return self
    def update(self, data):
        self._operation = "update"
        self._payload = data
        return self
    def eq(self, k, v):
        self._filters[k] = v
        return self
    def lte(self, k, v): return self
    def order(self, *args, **kwargs): return self
    def limit(self, n): return self
    def single(self):
        self._single = True
        return self

    def execute(self):
        if self._operation == "insert":
            self._table.rows.append(dict(self._payload))
            return FakeSupabaseResponse(self._payload)
        if self._operation == "update":
            for row in self._table.rows:
                if all(row.get(k) == v for k, v in self._filters.items()):
                    row.update(self._payload or {})
            return FakeSupabaseResponse(None)
        # select
        results = [r for r in self._table.rows if all(r.get(k) == v for k, v in self._filters.items())]
        if self._single:
            return FakeSupabaseResponse(results[0] if results else None)
        return FakeSupabaseResponse(results)


class FakeSupabaseTable:
    def __init__(self, rows=None):
        self.rows = rows or []

    def select(self, *args):
        return FakeSupabaseQuery(self, "select")
    def insert(self, data):
        return FakeSupabaseQuery(self, "insert").insert(data)
    def update(self, data):
        return FakeSupabaseQuery(self, "update").update(data)


class FakeSupabaseClient:
    def __init__(self, tables=None):
        self._tables = {}
        if tables:
            for name, rows in tables.items():
                self._tables[name] = FakeSupabaseTable(list(rows))

    def table(self, name):
        if name not in self._tables:
            self._tables[name] = FakeSupabaseTable()
        return self._tables[name]


# === Tests ===

class TestWorkerIdentity:

    def test_worker_id_returns_string(self):
        wid = worker_id()
        assert isinstance(wid, str)
        assert len(wid) > 0

    def test_worker_id_is_consistent(self):
        assert worker_id() == worker_id()


class TestClaimQueueRecord:

    @pytest.mark.asyncio
    async def test_claim_returns_none_when_empty(self, monkeypatch):
        fake_sb = FakeSupabaseClient({"agent_task_queue": []})
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        record = await claim_next_queue_record()
        assert record is None


class TestProcessQueueRecord:

    @pytest.mark.asyncio
    async def test_process_missing_task_id_marks_processed(self, monkeypatch):
        queue_record = {"id": "q1", "task_id": None, "status": "processing"}

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": []
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        await process_queue_record(queue_record)

        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"

    @pytest.mark.asyncio
    async def test_process_missing_task_marks_processed(self, monkeypatch):
        queue_record = {"id": "q1", "task_id": "t_nonexistent", "status": "processing"}

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": []
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        await process_queue_record(queue_record)

        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"

    @pytest.mark.asyncio
    async def test_process_successful_task(self, monkeypatch):
        queue_record = {"id": "q1", "task_id": "t1", "status": "processing", "attempts": 0, "max_attempts": 3}
        task_data = {"id": "t1", "agent_type": "bookkeeper", "user_id": "u1", "task": "Test", "context": {}, "status": "queued", "started_at": None}

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": [task_data],
            "agent_task_events": [],
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        class FakeRuntime:
            def __init__(self, agent_type, user_id): pass
            async def execute(self, task, context, task_id=None):
                return {"success": True, "result": "Done"}

        monkeypatch.setattr("app.workers.task_worker.AgentRuntime", FakeRuntime)

        await process_queue_record(queue_record)

        q = fake_sb.table("agent_task_queue").rows[0]
        assert q["status"] == "processed"

        t = fake_sb.table("agent_tasks").rows[0]
        assert t["status"] == "completed"

    @pytest.mark.asyncio
    async def test_process_unknown_agent_type_fails(self, monkeypatch):
        queue_record = {"id": "q1", "task_id": "t1", "status": "processing", "attempts": 0, "max_attempts": 3}
        task_data = {"id": "t1", "agent_type": "nonexistent_agent", "user_id": "u1", "task": "Test", "context": {}, "status": "queued"}

        fake_sb = FakeSupabaseClient({
            "agent_task_queue": [queue_record],
            "agent_tasks": [task_data],
            "agent_task_events": [],
        })
        monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: fake_sb)

        await process_queue_record(queue_record)

        t = fake_sb.table("agent_tasks").rows[0]
        assert t["status"] == "failed"
        assert t["failure_code"] == "UNKNOWN_AGENT"
