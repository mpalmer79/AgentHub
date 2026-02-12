import pytest
from app.agents.registry import AgentType


@pytest.mark.asyncio
async def test_advisory_lock_blocks_second_worker(monkeypatch):
    import app.api.agents as api

    class FakeResult:
        def __init__(self, data):
            self.data = data

    class FakeTable:
        def __init__(self):
            self.row = {"id": "t1", "status": "pending"}
            self.updates = []

        def select(self, *_): return self
        def eq(self, *_): return self
        def single(self): return self
        def order(self, *_ , **__): return self
        def limit(self, *_): return self

        def update(self, payload):
            self.updates.append(payload)
            if "status" in payload:
                self.row["status"] = payload["status"]
            return self

        def execute(self):
            return FakeResult(self.row)

        def insert(self, *_):
            return FakeResult([{"id": "t1"}])

    class FakeSupabase:
        def __init__(self):
            self.agent_tasks = FakeTable()
            self.lock_calls = 0

        def table(self, name):
            return self.agent_tasks

        def rpc(self, fn, params):
            if fn == "agent_task_try_lock":
                self.lock_calls += 1
                return FakeResult(True if self.lock_calls == 1 else False)
            if fn == "agent_task_unlock":
                return FakeResult(True)
            return FakeResult(None)

    fake_sb = FakeSupabase()
    monkeypatch.setattr(api, "get_supabase", lambda: fake_sb)

    class FakeRuntime:
        async def execute(self, *_ , **__):
            return {"success": True, "result": "ok"}

    import app.agents.runtime as rt
    monkeypatch.setattr(rt, "AgentRuntime", lambda *a, **k: FakeRuntime())

    await api.execute_agent_task("t1", AgentType.BOOKKEEPER, "task", {}, "u1")
    await api.execute_agent_task("t1", AgentType.BOOKKEEPER, "task", {}, "u1")

    assert fake_sb.lock_calls == 2
    assert any(u.get("status") == "running" for u in fake_sb.agent_tasks.updates)
