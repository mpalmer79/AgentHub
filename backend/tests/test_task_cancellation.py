import pytest
from app.agents.registry import AgentType


class FakeTable:
    def __init__(self):
        self.rows = {}

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


class FakeSupabase:
    def __init__(self, row):
        self.table_obj = FakeTable()
        self.table_obj.rows[row["id"]] = row

    def table(self, _):
        return self.table_obj


@pytest.mark.asyncio
async def test_cancel_running_task(monkeypatch):
    import app.api.agents as api

    fake_sb = FakeSupabase({
        "id": "t1",
        "status": "running",
        "created_at": "t0",
        "started_at": "t1",
        "completed_at": None,
        "result": None,
        "error": None,
    })

    monkeypatch.setattr(api, "get_supabase", lambda: fake_sb)

    response = await api.cancel_task("t1")
    assert response["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_prevents_completion(monkeypatch):
    import app.api.agents as api

    fake_sb = FakeSupabase({
        "id": "t2",
        "status": "pending",
        "created_at": "t0",
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
    })

    monkeypatch.setattr(api, "get_supabase", lambda: fake_sb)

    class FakeRuntime:
        async def execute(self, task, context):
            fake_sb.table_obj.rows["t2"]["status"] = "cancelled"
            return {"should": "not-save"}

    import app.agents.runtime as rt
    monkeypatch.setattr(rt, "AgentRuntime", lambda *a, **k: FakeRuntime())

    await api.execute_agent_task(
        "t2",
        AgentType.BOOKKEEPER,
        "work",
        {},
        "u1",
    )

    assert fake_sb.table_obj.rows["t2"]["status"] == "cancelled"
