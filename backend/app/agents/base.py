from typing import Dict, Any, Protocol
from app.agents.registry import AgentType


class ToolsInterface(Protocol):
    """Protocol for agent tools"""
    user_id: str


class AgentConfig:
    """Configuration for an agent"""
    def __init__(self, agent_type: AgentType, user_id: str):
        self.agent_type = agent_type
        self.user_id = user_id
