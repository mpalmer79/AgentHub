import pytest
from fastapi.testclient import TestClient

from app.main import app


class FakeQuery:
    def __init__(self, table, filters=None):
        self._table = table
        self._filters = filters or {}

    def eq(self, key, value):
        self._filters[key] = value
        return self

    def select(self, *_):
        return self

    def execute(self):
        row_id = self._filters.get("id")
        if row_id in self._table._rows:
            return type("Result", (), {"data": [self._table._rows[row_id]]})
        return type("Result", (), {"data": []})


class FakeTable:
    def __init__(self):
        self._rows = {}

    def seed(self, row_id, data):
        self._rows[row_id] = data

    def select(self, *_):
        return FakeQuery(self)


class FakeSupabase:
    def __init__(self):
        self._tables = {"agent_tasks": FakeTable()}

    def table(self, name):
        return self._tables[name]


@pytest.fixture
def client(monkeypatch):
    fake_sb = FakeSupabase()

    fake_sb.table("agent_tasks").seed(
        "task_123",
        {
            "id": "task_123",
            "status": "completed",
            "result": {"success": True},
            "error": None,
        },
    )

    import app.api.agents as agents_api
    monkeypatch.setattr(agents_api, "get_supabase", lambda: fake_sb)

    return TestClient(app)


def test_get_agent_task_status_success(client):
    response = client.get("/api/agents/task_123")

    assert response.status_code == 200
    body = response.json()

    assert body["task_id"] == "task_123"
    assert body["status"] == "completed"
    assert body["result"] == {"success": True}
    assert body["error"] is None


def test_get_agent_task_status_not_found(client):
    response = client.get("/api/agents/missing_task")

    assert response.status_code == 404
    assert response.json()["detail"] == "Agent task not found"
