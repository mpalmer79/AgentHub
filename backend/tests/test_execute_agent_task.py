import pytest

from app.agents.registry import AgentType


class FakeQuery:
    def __init__(self, table, op=None, payload=None):
        self._table = table
        self._op = op
        self._payload = payload or {}
        self._filters = {}

    def update(self, payload: dict):
        return FakeQuery(self._table, op="update", payload=payload)

    def eq(self, key: str, value):
        self._filters[key] = value
        return self

    def execute(self):
        if self._op == "update":
            row_id = self._filters.get("id")
            if row_id is None or row_id not in self._table._rows:
                return type("Result", (), {"data": None})
            self._table._rows[row_id].update(self._payload)
            return type("Result", (), {"data": [self._table._rows[row_id]]})
        return type("Result", (), {"data": None})


class FakeTable:
    def __init__(self):
        self._rows = {}

    def seed(self, row_id: str, data: dict):
        self._rows[row_id] = dict(data)

    def update(self, payload: dict):
        return FakeQuery(self, op="update", payload=payload)


class FakeSupabase:
    def __init__(self):
        self._tables = {"agent_tasks": FakeTable()}

    def table(self, name: str):
        if name not in self._tables:
            self._tables[name] = FakeTable()
        return self._tables[name]


@pytest.mark.asyncio
async def test_execute_agent_task_marks_completed_and_saves_result(monkeypatch):
    # Import inside the test so monkeypatching works cleanly
    import app.api.agents as agents_api

    fake_sb = FakeSupabase()
    fake_sb.table("agent_tasks").seed(
        "task_1",
        {
            "id": "task_1",
            "status": "pending",
            "result": None,
            "error": None,
        },
    )

    monkeypatch.setattr(agents_api, "get_supabase", lambda: fake_sb)

    class FakeRuntime:
        def __init__(self, agent_type, user_id):
            self.agent_type = agent_type
            self.user_id = user_id

        async def execute(self, task, context):
            return {"success": True, "result": "ok"}

    # Patch the runtime used inside execute_agent_task
    import app.agents.runtime as runtime_module
    monkeypatch.setattr(runtime_module, "AgentRuntime", FakeRuntime)

    # Act
    await agents_api.execute_agent_task(
        task_id="task_1",
        agent_type=AgentType.BOOKKEEPER,
        task="do work",
        context={"x": 1},
        user_id="user_123",
    )

    # Assert: worker should have updated row
    row = fake_sb.table("agent_tasks")._rows["task_1"]
    assert row["status"] == "completed"
    assert row["result"] == {"success": True, "result": "ok"}
    assert row.get("error") in (None, "")
