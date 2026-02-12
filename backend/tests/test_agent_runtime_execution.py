import pytest

from app.agents.runtime import AgentRuntime
from app.agents.registry import AgentType


class FakeTextBlock:
    type = "text"

    def __init__(self, text: str):
        self.text = text

    def model_dump(self):
        return {"type": "text", "text": self.text}


class FakeToolUseBlock:
    type = "tool_use"

    def __init__(self, tool_id: str, name: str, input_data: dict):
        self.id = tool_id
        self.name = name
        self.input = input_data

    def model_dump(self):
        return {"type": "tool_use", "id": self.id, "name": self.name, "input": self.input}


class FakeResponse:
    def __init__(self, stop_reason: str, content: list):
        self.stop_reason = stop_reason
        self.content = content


class FakeMessages:
    def __init__(self, responses: list[FakeResponse]):
        self._responses = list(responses)

    def create(self, **kwargs):
        if not self._responses:
            raise AssertionError("FakeMessages.create called more times than expected.")
        return self._responses.pop(0)


class FakeAnthropicClient:
    def __init__(self, responses: list[FakeResponse]):
        self.messages = FakeMessages(responses)


@pytest.mark.asyncio
async def test_agent_runtime_end_turn_returns_success(monkeypatch):
    # Arrange: Claude returns end_turn immediately with a text block
    responses = [
        FakeResponse(
            stop_reason="end_turn",
            content=[FakeTextBlock("Done.")]
        )
    ]

    import app.agents.runtime as runtime_module

    monkeypatch.setattr(
        runtime_module.anthropic,
        "Anthropic",
        lambda api_key: FakeAnthropicClient(responses)
    )

    runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

    # Act
    result = await runtime.execute("Say hi", context={})

    # Assert
    assert result["success"] is True
    assert result["result"] == "Done."
    assert result["iterations"] == 1
    assert len(result["execution_log"]) == 1


@pytest.mark.asyncio
async def test_agent_runtime_tool_use_executes_tool_and_continues(monkeypatch):
    # Arrange: First Claude response requests a tool call, second ends the turn
    responses = [
        FakeResponse(
            stop_reason="tool_use",
            content=[
                FakeToolUseBlock(
                    tool_id="tool_1",
                    name="get_transactions",
                    input_data={"start_date": "2026-01-01", "end_date": "2026-01-31"}
                )
            ],
        ),
        FakeResponse(
            stop_reason="end_turn",
            content=[FakeTextBlock("Report complete.")]
        )
    ]

    import app.agents.runtime as runtime_module

    monkeypatch.setattr(
        runtime_module.anthropic,
        "Anthropic",
        lambda api_key: FakeAnthropicClient(responses)
    )

    runtime = AgentRuntime(agent_type=AgentType.BOOKKEEPER, user_id="user_123")

    tool_calls = []

    async def fake_execute_tool(tool_name: str, tool_input: dict):
        tool_calls.append((tool_name, tool_input))
        return {"ok": True}

    monkeypatch.setattr(runtime, "_execute_tool", fake_execute_tool)

    # Act
    result = await runtime.execute("Generate report", context={"foo": "bar"})

    # Assert
    assert result["success"] is True
    assert result["result"] == "Report complete."
    assert result["iterations"] == 2
    assert len(result["execution_log"]) == 2

    assert tool_calls == [
        ("get_transactions", {"start_date": "2026-01-01", "end_date": "2026-01-31"})
    ]
