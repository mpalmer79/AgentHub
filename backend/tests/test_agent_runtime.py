"""
Tests for AgentRuntime execution.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.agents.runtime import AgentRuntime
from app.agents.registry import AgentType


# === Fake classes (defined here, not imported) ===

class FakeTextBlock:
    type = "text"
    def __init__(self, text: str):
        self.text = text


class FakeToolUseBlock:
    type = "tool_use"
    def __init__(self, tool_id: str, name: str, input_data: dict):
        self.id = tool_id
        self.name = name
        self.input = input_data


class FakeUsage:
    def __init__(self, input_tokens: int = 100, output_tokens: int = 50):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class FakeClaudeResponse:
    def __init__(self, stop_reason: str, content: list):
        self.stop_reason = stop_reason
        self.content = content
        self.usage = FakeUsage()


class FakeClaudeMessages:
    def __init__(self, responses: list):
        self._responses = list(responses)

    def create(self, **kwargs):
        if not self._responses:
            raise AssertionError("No more responses")
        return self._responses.pop(0)


class FakeAnthropicClient:
    def __init__(self, responses: list):
        self.messages = FakeClaudeMessages(responses)


class FakeSupabaseResponse:
    def __init__(self, data=None):
        self.data = data


class FakeSupabaseTable:
    def __init__(self):
        self.rows = []

    def select(self, *args): return self
    def insert(self, data):
        self.rows.append(data)
        return self
    def update(self, data): return self
    def eq(self, k, v): return self
    def single(self): return self
    def execute(self):
        return FakeSupabaseResponse(None)


class FakeSupabaseClient:
    def __init__(self):
        self._tables = {}

    def table(self, name):
        if name not in self._tables:
            self._tables[name] = FakeSupabaseTable()
        return self._tables[name]


# === Tests ===

class TestAgentRuntimeBasic:

    @pytest.mark.asyncio
    async def test_end_turn_returns_success(self, monkeypatch):
        responses = [
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("Task completed successfully.")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient()
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")
        result = await runtime.execute("Categorize my transactions", context={})

        assert result["success"] is True
        assert result["result"] == "Task completed successfully."
        assert result["iterations"] == 1

    @pytest.mark.asyncio
    async def test_empty_response_still_succeeds(self, monkeypatch):
        responses = [
            FakeClaudeResponse(stop_reason="end_turn", content=[FakeTextBlock("")])
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient()
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")
        result = await runtime.execute("Test task", context={})

        assert result["success"] is True
        assert result["result"] == ""


class TestAgentRuntimeToolUse:

    @pytest.mark.asyncio
    async def test_tool_use_executes_and_continues(self, monkeypatch):
        responses = [
            FakeClaudeResponse(
                stop_reason="tool_use",
                content=[
                    FakeToolUseBlock("tool_1", "get_transactions",
                                     {"start_date": "2026-01-01", "end_date": "2026-01-31"})
                ],
            ),
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("Found 5 transactions.")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient()
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

        tool_calls = []
        async def tracking_execute(tool_name, tool_input):
            tool_calls.append((tool_name, tool_input))
            return {"transactions": [], "count": 5}

        runtime.executor.execute = tracking_execute

        result = await runtime.execute("Get January transactions", context={})

        assert result["success"] is True
        assert result["iterations"] == 2
        assert len(tool_calls) == 1
        assert tool_calls[0][0] == "get_transactions"


class TestAgentRuntimeMaxIterations:

    @pytest.mark.asyncio
    async def test_max_iterations_returns_failure(self, monkeypatch):
        responses = [
            FakeClaudeResponse(
                stop_reason="tool_use",
                content=[FakeToolUseBlock(f"t{i}", "get_transactions", {})]
            )
            for i in range(15)
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient()
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

        async def fake_execute(tool_name, tool_input):
            return {"ok": True}
        runtime.executor.execute = fake_execute

        result = await runtime.execute("Infinite task", context={})

        assert result["success"] is False
        assert "Max iterations" in result["error"]
        assert result["iterations"] == 10
