"""Tests for prompt versioning and system-prompt assembly."""

import re

from app.agents.prompts.agent_prompts import (
    AGENT_PROMPTS,
    PROMPT_VERSION,
    build_system_prompt,
)
from app.agents.registry import AgentType


def test_prompt_version_is_dated_string():
    assert re.match(r"^\d{4}-\d{2}-\d{2}\.\d+$", PROMPT_VERSION), (
        f"PROMPT_VERSION must look like 'YYYY-MM-DD.N', got {PROMPT_VERSION!r}"
    )


def test_every_agent_has_a_prompt():
    for agent_type in AgentType:
        assert agent_type in AGENT_PROMPTS, f"Missing prompt for {agent_type}"


def test_system_prompt_includes_agent_name_and_guidelines():
    prompt = build_system_prompt(AgentType.BOOKKEEPER)
    assert "Bookkeeper" in prompt
    assert "categorize" in prompt.lower()


def test_system_prompt_includes_current_utc_time():
    prompt = build_system_prompt(AgentType.BOOKKEEPER)
    assert "UTC" in prompt
