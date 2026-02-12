"""
Tests for AgentRuntime execution.

Tests the core agent execution loop including:
- Simple end_turn responses
- Tool use and continuation
- Max iterations handling
- Event emission
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.agents.runtime import AgentRuntime
from app.agents.registry import AgentType
from tests.conftest import (
    FakeClaudeResponse, FakeTextBlock, FakeToolUseBlock,
    FakeAnthropicClient, FakeSupabaseClient
)


class TestAgentRuntimeBasic:
    """Basic runtime execution tests."""

    @pytest.mark.asyncio
    async def test_end_turn_returns_success(self, monkeypatch):
        """When Claude returns end_turn, runtime should return success."""
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

        # Mock Supabase for event emission
        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")
        result = await runtime.execute("Categorize my transactions", context={})

        assert result["success"] is True
        assert result["result"] == "Task completed successfully."
        assert result["iterations"] == 1

    @pytest.mark.asyncio
    async def test_empty_response_still_succeeds(self, monkeypatch):
        """Runtime handles empty text blocks gracefully."""
        responses = [
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")
        result = await runtime.execute("Test task", context={})

        assert result["success"] is True
        assert result["result"] == ""


class TestAgentRuntimeToolUse:
    """Tool use execution tests."""

    @pytest.mark.asyncio
    async def test_tool_use_executes_and_continues(self, monkeypatch):
        """When Claude requests tool use, runtime executes tool and continues."""
        responses = [
            FakeClaudeResponse(
                stop_reason="tool_use",
                content=[
                    FakeToolUseBlock(
                        tool_id="tool_1",
                        name="get_transactions",
                        input_data={"start_date": "2026-01-01", "end_date": "2026-01-31"}
                    )
                ],
            ),
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("Found 5 transactions totaling $1,234.")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

        # Track tool calls
        tool_calls = []
        original_execute = runtime.executor.execute

        async def tracking_execute(tool_name: str, tool_input: dict):
            tool_calls.append((tool_name, tool_input))
            return {"transactions": [], "count": 5, "total": 1234}

        runtime.executor.execute = tracking_execute

        result = await runtime.execute("Get my January transactions", context={})

        assert result["success"] is True
        assert result["iterations"] == 2
        assert len(tool_calls) == 1
        assert tool_calls[0][0] == "get_transactions"
        assert tool_calls[0][1]["start_date"] == "2026-01-01"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_in_sequence(self, monkeypatch):
        """Runtime handles multiple sequential tool calls."""
        responses = [
            FakeClaudeResponse(
                stop_reason="tool_use",
                content=[FakeToolUseBlock("t1", "get_accounts", {})]
            ),
            FakeClaudeResponse(
                stop_reason="tool_use",
                content=[FakeToolUseBlock("t2", "get_transactions", {"account_id": "123"})]
            ),
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("Analysis complete.")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

        tool_calls = []
        async def tracking_execute(tool_name: str, tool_input: dict):
            tool_calls.append(tool_name)
            return {"ok": True}
        runtime.executor.execute = tracking_execute

        result = await runtime.execute("Analyze my accounts", context={})

        assert result["success"] is True
        assert result["iterations"] == 3
        assert tool_calls == ["get_accounts", "get_transactions"]


class TestAgentRuntimeMaxIterations:
    """Max iterations handling tests."""

    @pytest.mark.asyncio
    async def test_max_iterations_returns_failure(self, monkeypatch):
        """When max iterations reached, runtime returns failure."""
        # Create enough tool_use responses to exceed max_iterations (10)
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

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

        async def fake_execute(tool_name: str, tool_input: dict):
            return {"ok": True}
        runtime.executor.execute = fake_execute

        result = await runtime.execute("Infinite task", context={})

        assert result["success"] is False
        assert "Max iterations" in result["error"]
        assert result["iterations"] == 10


class TestAgentRuntimeEventEmission:
    """Event emission tests."""

    @pytest.mark.asyncio
    async def test_emits_task_started_event(self, monkeypatch):
        """Runtime emits task_started event when task_id provided."""
        responses = [
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("Done.")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")
        await runtime.execute("Test task", context={}, task_id="task_001")

        # Check events were emitted
        events = fake_sb.table("agent_task_events").rows
        event_types = [e["event_type"] for e in events]

        assert "task_started" in event_types
        assert "task_completed" in event_types

    @pytest.mark.asyncio
    async def test_emits_tool_called_events(self, monkeypatch):
        """Runtime emits tool_called events for tool use."""
        responses = [
            FakeClaudeResponse(
                stop_reason="tool_use",
                content=[FakeToolUseBlock("t1", "get_accounts", {})]
            ),
            FakeClaudeResponse(
                stop_reason="end_turn",
                content=[FakeTextBlock("Done.")]
            )
        ]

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: FakeAnthropicClient(responses)
        )

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

        async def fake_execute(tool_name: str, tool_input: dict):
            return {"ok": True}
        runtime.executor.execute = fake_execute

        await runtime.execute("Test", context={}, task_id="task_002")

        events = fake_sb.table("agent_task_events").rows
        event_types = [e["event_type"] for e in events]

        assert "tool_called" in event_types
        assert "tool_result" in event_types


class TestAgentRuntimeContext:
    """Context handling tests."""

    @pytest.mark.asyncio
    async def test_context_included_in_message(self, monkeypatch):
        """Context is appended to the user message."""
        captured_messages = []

        class CapturingMessages:
            def create(self, **kwargs):
                captured_messages.append(kwargs.get("messages", []))
                return FakeClaudeResponse("end_turn", [FakeTextBlock("Done")])

        class CapturingClient:
            messages = CapturingMessages()

        monkeypatch.setattr(
            "app.agents.runtime.anthropic.Anthropic",
            lambda api_key: CapturingClient()
        )

        fake_sb = FakeSupabaseClient({"agent_task_events": [], "agent_tasks": []})
        monkeypatch.setattr("app.agents.runtime.get_supabase", lambda: fake_sb)

        runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")
        await runtime.execute(
            "Process this",
            context={"account_id": "acc_123", "date_range": "Q1"}
        )

        assert len(captured_messages) == 1
        user_content = captured_messages[0][0]["content"]
        assert "account_id" in user_content
        assert "acc_123" in user_content
