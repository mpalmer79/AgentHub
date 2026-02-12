import types
import pytest

from app.workers.task_worker import process_queue_record

class FakeTable:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self._filters = {}
        self._single = False
        self._update = None
        self._select = None

    def select(self, _):
        return self

    def update(self, payload):
        self._update = payload
        return self

    def eq(self, k, v):
        self._filters[k] = v
        return self

    def single(self):
        self._single = True
        return self

    def execute(self):
        # crude in-memory operations for just what we need
        if self._update is not None:
            table = self.db[self.name]
            for row in table:
                ok = all(row.get(k) == v for k, v in self._filters.items())
                if ok:
                    row.update(self._update)
            return types.SimpleNamespace(data=None)

        # select
        table = self.db[self.name]
        rows = [r for r in table if all(r.get(k) == v for k, v in self._filters.items())]
        if self._single:
            return types.SimpleNamespace(data=(rows[0] if rows else None))
        return types.SimpleNamespace(data=rows)

class FakeSupabase:
    def __init__(self, db):
        self.db = db
    def table(self, name):
        return FakeTable(self.db, name)

@pytest.mark.asyncio
async def test_retryable_failure_requeues(monkeypatch):
    # Arrange in-memory db
    db = {
        "agent_task_queue": [{
            "id": "q1",
            "task_id": "t1",
            "attempts": 0,
            "max_attempts": 3,
            "status": "processing",
        }],
        "agent_tasks": [{
            "id": "t1",
            "agent_type": "email_agent",
            "user_id": "u1",
            "task": "do something",
            "context": {},
            "status": "running",
        }],
    }

    # Patch get_supabase_admin
    monkeypatch.setattr("app.workers.task_worker.get_supabase_admin", lambda: FakeSupabase(db))

    # Patch AgentRuntime.execute to throw retryable error
    class FakeRuntime:
        def __init__(self, *args, **kwargs): ...
        async def execute(self, *args, **kwargs):
            raise RuntimeError("429 too many requests")

    monkeypatch.setattr("app.workers.task_worker.AgentRuntime", FakeRuntime)

    # Act
    await process_queue_record(db["agent_task_queue"][0])

    # Assert queue is back to queued with attempts incremented
    q = db["agent_task_queue"][0]
    assert q["status"] == "queued"
    assert q["attempts"] == 1
    assert "next_run_at" in q
