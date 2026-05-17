"""Tiny eval harness for agents.

Goal: catch behavior regressions before customers do, without paying
to call Claude on every CI run.

A `Case` is a single deterministic scripted scenario: you control the
sequence of Claude responses (text + tool calls) and the expected
tool invocations, then assert on the final result. The harness wires
a `FakeAnthropic` into `AgentRuntime` and runs the agent end-to-end.

For live evals against the real API, set ANTHROPIC_API_KEY and pass
`live=True` to `run_case` — this is intentionally opt-in so CI stays
deterministic and free.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from app.agents.registry import AgentType
from app.agents.runtime import AgentRuntime


# ---------- Fake Anthropic client ----------


class _FakeUsage:
    def __init__(self, input_tokens: int = 100, output_tokens: int = 50):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _FakeTextBlock:
    type = "text"

    def __init__(self, text: str):
        self.text = text


class _FakeToolUseBlock:
    type = "tool_use"

    def __init__(self, tool_id: str, name: str, input_data: dict):
        self.id = tool_id
        self.name = name
        self.input = input_data


class _FakeResponse:
    def __init__(self, stop_reason: str, content: list, usage: _FakeUsage):
        self.stop_reason = stop_reason
        self.content = content
        self.usage = usage


class _FakeMessages:
    def __init__(self, scripted: list[_FakeResponse]):
        self._scripted = list(scripted)

    def create(self, **_):
        if not self._scripted:
            raise AssertionError("Eval ran out of scripted Claude responses.")
        return self._scripted.pop(0)


class _FakeAnthropic:
    def __init__(self, scripted: list[_FakeResponse]):
        self.messages = _FakeMessages(scripted)


def text(s: str, *, in_tok: int = 100, out_tok: int = 50) -> _FakeResponse:
    return _FakeResponse("end_turn", [_FakeTextBlock(s)], _FakeUsage(in_tok, out_tok))


def tool_call(
    tool_id: str, name: str, args: dict, *, in_tok: int = 80, out_tok: int = 40
) -> _FakeResponse:
    return _FakeResponse(
        "tool_use", [_FakeToolUseBlock(tool_id, name, args)], _FakeUsage(in_tok, out_tok)
    )


# ---------- Fake Supabase (only what the runtime touches) ----------


class _FakeResult:
    data = None


class _FakeTable:
    def __init__(self):
        self.rows: list = []

    def select(self, *_a, **_k):
        return self

    def insert(self, data):
        self.rows.append(data)
        return self

    def update(self, _data):
        return self

    def eq(self, *_a, **_k):
        return self

    def single(self):
        return self

    def execute(self):
        return _FakeResult()


class _FakeSupabase:
    def __init__(self):
        self._tables: dict[str, _FakeTable] = {}

    def table(self, name: str) -> _FakeTable:
        return self._tables.setdefault(name, _FakeTable())


# ---------- Public API ----------


@dataclass
class CaseResult:
    name: str
    passed: bool
    detail: str = ""
    tool_calls: list[tuple[str, dict]] = field(default_factory=list)
    iterations: int = 0


@dataclass
class Case:
    name: str
    agent: AgentType
    task: str
    scripted_responses: list[_FakeResponse]
    tool_responses: dict[str, Any]
    expect_success: bool = True
    expect_tools: list[str] = field(default_factory=list)
    assert_fn: Optional[Callable[[dict], None]] = None


def run_case(case: Case, *, monkeypatch=None) -> CaseResult:
    """Execute one case synchronously. Returns a CaseResult."""
    import app.agents.runtime as runtime_mod

    real_anthropic_cls = runtime_mod.anthropic.Anthropic
    real_get_supabase = runtime_mod.get_supabase

    fake_supabase = _FakeSupabase()
    runtime_mod.anthropic.Anthropic = lambda **_kw: _FakeAnthropic(case.scripted_responses)  # type: ignore
    runtime_mod.get_supabase = lambda *_a, **_k: fake_supabase  # type: ignore

    try:
        rt = AgentRuntime(agent_type=case.agent, user_id="eval_user")

        observed_calls: list[tuple[str, dict]] = []

        async def fake_tool_execute(tool_name: str, tool_input: dict):
            observed_calls.append((tool_name, tool_input))
            if tool_name not in case.tool_responses:
                return {"error": f"eval has no scripted response for tool '{tool_name}'"}
            return case.tool_responses[tool_name]

        rt.executor.execute = fake_tool_execute  # type: ignore

        result = asyncio.run(rt.execute(case.task, context={}))

        if bool(result.get("success")) != case.expect_success:
            return CaseResult(
                name=case.name,
                passed=False,
                detail=f"expected success={case.expect_success}, got {result}",
                tool_calls=observed_calls,
                iterations=int(result.get("iterations") or 0),
            )

        observed_tool_names = [n for n, _ in observed_calls]
        for expected in case.expect_tools:
            if expected not in observed_tool_names:
                return CaseResult(
                    name=case.name,
                    passed=False,
                    detail=f"expected tool '{expected}' to be called; got {observed_tool_names}",
                    tool_calls=observed_calls,
                    iterations=int(result.get("iterations") or 0),
                )

        if case.assert_fn:
            try:
                case.assert_fn(result)
            except AssertionError as exc:
                return CaseResult(
                    name=case.name,
                    passed=False,
                    detail=f"assert_fn failed: {exc}",
                    tool_calls=observed_calls,
                    iterations=int(result.get("iterations") or 0),
                )

        return CaseResult(
            name=case.name,
            passed=True,
            tool_calls=observed_calls,
            iterations=int(result.get("iterations") or 0),
        )
    finally:
        runtime_mod.anthropic.Anthropic = real_anthropic_cls  # type: ignore
        runtime_mod.get_supabase = real_get_supabase  # type: ignore


def run_suite(cases: list[Case]) -> tuple[int, int, list[CaseResult]]:
    """Run all cases. Returns (passed, total, results)."""
    results = [run_case(c) for c in cases]
    passed = sum(1 for r in results if r.passed)
    return passed, len(results), results


def print_results(results: list[CaseResult]) -> None:
    for r in results:
        marker = "PASS" if r.passed else "FAIL"
        line = f"[{marker}] {r.name}  (iters={r.iterations}, tools={len(r.tool_calls)})"
        print(line)
        if not r.passed:
            print(f"        {r.detail}")
