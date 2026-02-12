import pytest
from app.agents.registry import AgentType


class FakeTable:
    def __init__(self):
        self.rows = {}

    def insert(self, data):
        self.rows[data["id"]] = dict(data)
        return self

    def select(self, *_):
        return self

    def update(self, payload):
        self._payload = payload
        return self

    def eq(self, key, value):
        self._id = value
        return self

    def execute(self):
        if hasattr(self, "_payload"):
            self.rows[self._id].update(self._payload)
            return type("R", (), {"data": [self.rows[self._id]]})
        return type("R", (), {"data": [self.rows[self._id]]})


class FakeSupabase:
    def __init__(self):
        self.table_obj = FakeTable()

    def table(self, _):
        return self.table_obj


@pytest.mark.asyncio
async def test_retry_protection_and_timestamps(monkeypatch):
    import app.api.agents as agents_api

    fake_sb = FakeSupabase()

    fake_sb.table_obj.rows["task_1"] = {
        "id": "task_1",
        "status": "pending",
        "created_at": "t0",
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
    }

    monkeypatch.setattr(agents_api, "get_supabase", lambda: fake_sb)

    class FakeRuntime:
        async def execute(self, task, context):
            return {"ok": True}

    import app.agents.runtime as runtime_module
    monkeypatch.setattr(runtime_module, "AgentRuntime", lambda *args, **kw: FakeRuntime())

    # First execution
    await agents_api.execute_agent_task(
        task_id="task_1",
        agent_type=AgentType.BOOKKEEPER,
        task="do work",
        context={},
        user_id="u1",
    )

    row = fake_sb.table_obj.rows["task_1"]
    assert row["status"] == "completed"
    assert row["started_at"] is not None
    assert row["completed_at"] is not None

    started_at = row["started_at"]

    # Second execution attempt (should be ignored)
    await agents_api.execute_agent_task(
        task_id="task_1",
        agent_type=AgentType.BOOKKEEPER,
        task="do work",
        context={},
        user_id="u1",
    )

    row_after = fake_sb.table_obj.rows["task_1"]
    assert row_after["started_at"] == started_at
