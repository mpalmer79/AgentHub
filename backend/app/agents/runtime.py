from typing import Dict, Any
import anthropic
import time

from app.core.config import settings
from app.core.database import get_supabase
from app.agents.registry import AgentType, AGENT_REGISTRY
from app.agents.prompts.agent_prompts import build_system_prompt
from app.agents.schemas import get_tools_schema
from app.agents.executors.tool_executor import ToolExecutor

# Tool imports
from app.agents.tools.quickbooks import QuickBooksTools
from app.agents.tools.gmail import GmailTools
from app.agents.tools.calendar import GoogleCalendarTools
from app.agents.tools.hiring import HiringTools
from app.agents.tools.cashflow import CashFlowTools
from app.agents.tools.reputation import ReputationTools
from app.agents.tools.customer_care import CustomerCareTools
from app.agents.tools.social_pilot import SocialPilotTools
from app.agents.tools.compliance import ComplianceTools
from app.agents.tools.vendor import VendorTools
from app.agents.tools.proposal import ProposalTools
from app.agents.tools.inventory import InventoryTools


TOOLS_REGISTRY: Dict[AgentType, tuple] = {
    AgentType.BOOKKEEPER: ("quickbooks", QuickBooksTools),
    AgentType.INBOX_COMMANDER: ("gmail", GmailTools),
    AgentType.APPOINTMENT: ("calendar", GoogleCalendarTools),
    AgentType.HIRE_WELL: ("hiring", HiringTools),
    AgentType.CASHFLOW_COMMANDER: ("cashflow", CashFlowTools),
    AgentType.REPUTATION_SHIELD: ("reputation", ReputationTools),
    AgentType.CUSTOMER_CARE: ("customer_care", CustomerCareTools),
    AgentType.SOCIAL_PILOT: ("social_pilot", SocialPilotTools),
    AgentType.COMPLIANCE_GUARD: ("compliance", ComplianceTools),
    AgentType.VENDOR_NEGOTIATOR: ("vendor", VendorTools),
    AgentType.PROPOSAL_PRO: ("proposal", ProposalTools),
    AgentType.INVENTORY_IQ: ("inventory", InventoryTools),
}


class AgentRuntime:
    def __init__(self, agent_type: AgentType, user_id: str):
        self.agent_type = agent_type
        self.user_id = user_id
        self.agent_info = AGENT_REGISTRY.get(agent_type, {})
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.tools = self._initialize_tools()
        self.executor = ToolExecutor(agent_type, self.tools)

    def _initialize_tools(self) -> Dict[str, Any]:
        tools = {}
        if self.agent_type in TOOLS_REGISTRY:
            key, ToolClass = TOOLS_REGISTRY[self.agent_type]
            tools[key] = ToolClass(self.user_id)
        return tools

    def _emit_event(self, task_id: str, event_type: str, payload: dict = None):
        supabase = get_supabase()
        supabase.table("agent_task_events").insert({
            "task_id": task_id,
            "event_type": event_type,
            "payload": payload or {},
        }).execute()

    async def execute(self, task: str, context: Dict[str, Any], task_id: str = None) -> Dict[str, Any]:

        start_time = time.time()

        messages = [{"role": "user", "content": task}]
        if context:
            messages[0]["content"] += f"\n\nAdditional context:\n{context}"

        tools_schema = get_tools_schema(self.agent_type)

        max_iterations = 10
        iteration = 0

        if task_id:
            self._emit_event(task_id, "task_started", {
                "agent_type": self.agent_type.value
            })

        while iteration < max_iterations:
            iteration += 1

            if task_id:
                self._emit_event(task_id, "model_call_started", {
                    "iteration": iteration
                })

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=build_system_prompt(self.agent_type),
                tools=tools_schema if tools_schema else None,
                messages=messages,
            )

            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "input_tokens", None) if usage else None
            output_tokens = getattr(usage, "output_tokens", None) if usage else None
            total_tokens = (input_tokens or 0) + (output_tokens or 0)

            if task_id:
                self._emit_event(task_id, "model_call_completed", {
                    "iteration": iteration,
                    "stop_reason": response.stop_reason,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                })

            # Completion
            if response.stop_reason == "end_turn":
                final_text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )

                duration_ms = int((time.time() - start_time) * 1000)

                if task_id:
                    supabase = get_supabase()
                    supabase.table("agent_tasks").update({
                        "duration_ms": duration_ms,
                        "model_provider": "anthropic",
                        "model_name": "claude-sonnet-4-20250514",
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": total_tokens,
                    }).eq("id", task_id).execute()

                    self._emit_event(task_id, "task_completed", {
                        "iterations": iteration,
                        "duration_ms": duration_ms
                    })

                return {
                    "success": True,
                    "result": final_text,
                    "iterations": iteration,
                }

            # Tool use
            if response.stop_reason == "tool_use":

                for block in response.content:
                    if block.type != "tool_use":
                        continue

                    if task_id:
                        self._emit_event(task_id, "tool_called", {
                            "tool_name": block.name,
                            "input": block.input,
                            "iteration": iteration
                        })

                    tool_result = await self.executor.execute(block.name, block.input)

                    if task_id:
                        self._emit_event(task_id, "tool_result", {
                            "tool_name": block.name,
                            "result_preview": str(tool_result)[:500]
                        })

                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(tool_result)
                        }]
                    })

                continue

            break

        duration_ms = int((time.time() - start_time) * 1000)

        if task_id:
            self._emit_event(task_id, "task_failed", {
                "reason": "max_iterations",
                "duration_ms": duration_ms
            })

        return {
            "success": False,
            "error": "Max iterations reached",
            "iterations": iteration,
        }
