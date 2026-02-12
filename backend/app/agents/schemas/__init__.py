from typing import List, Dict, Any
from app.agents.registry import AgentType

from .bookkeeper import get_bookkeeper_schema
from .inbox import get_inbox_schema
from .appointment import get_appointment_schema
from .hiring import get_hiring_schema
from .cashflow import get_cashflow_schema
from .reputation import get_reputation_schema
from .customer_care import get_customer_care_schema
from .social_pilot import get_social_pilot_schema
from .compliance import get_compliance_schema
from .vendor import get_vendor_schema
from .proposal import get_proposal_schema
from .inventory import get_inventory_schema


SCHEMA_REGISTRY: Dict[AgentType, callable] = {
    AgentType.BOOKKEEPER: get_bookkeeper_schema,
    AgentType.INBOX_COMMANDER: get_inbox_schema,
    AgentType.APPOINTMENT: get_appointment_schema,
    AgentType.HIRE_WELL: get_hiring_schema,
    AgentType.CASHFLOW_COMMANDER: get_cashflow_schema,
    AgentType.REPUTATION_SHIELD: get_reputation_schema,
    AgentType.CUSTOMER_CARE: get_customer_care_schema,
    AgentType.SOCIAL_PILOT: get_social_pilot_schema,
    AgentType.COMPLIANCE_GUARD: get_compliance_schema,
    AgentType.VENDOR_NEGOTIATOR: get_vendor_schema,
    AgentType.PROPOSAL_PRO: get_proposal_schema,
    AgentType.INVENTORY_IQ: get_inventory_schema,
}


def get_tools_schema(agent_type: AgentType) -> List[Dict[str, Any]]:
    """Get tool schemas for an agent type"""
    schema_fn = SCHEMA_REGISTRY.get(agent_type)
    if schema_fn:
        return schema_fn()
    return []
