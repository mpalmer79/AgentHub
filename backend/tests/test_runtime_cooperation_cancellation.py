import pytest
from app.agents.registry import AgentType


@pytest.mark.asyncio
async def test_runtime_stops_when_task_cancelled(monkeypatch):
    from app.agents.runtime import AgentRuntime

    class FakeResult:
        def __init__(self, data): self.data = data

    class FakeTable:
        def __init__(self):
            self.status = "cancelled"

        def select(self, *_): return self
        def eq(self, *_): return self
        def single(self): return self
        def execute(self): return FakeResult({"status": self.status})
        def insert(self, *_): return FakeResult([{"id": 1}])

    class FakeSupabase:
        def table(self, name):
            return FakeTable()

    import app.agents.runtime as runtime_module
    monkeypatch.setattr(runtime_module, "get_supabase", lambda: FakeSupabase())

    # Prevent real Anthropic call (should never be reached)
    class FakeMessages:
        def create(self, **kwargs):
            raise AssertionError("Model call should not occur after cancellation")

    class FakeClient:
        def __init__(self): self.messages = FakeMessages()

    monkeypatch.setattr(runtime_module.anthropic, "Anthropic", lambda api_key: FakeClient())

    runtime = AgentRuntime(AgentType.BOOKKEEPER, "u1")
    result = await runtime.execute("do work", {}, task_id="t1")

    assert result["success"] is False
    assert result["error"] == "Task cancelled"
