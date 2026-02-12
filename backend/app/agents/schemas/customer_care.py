from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, boolean_prop


def get_customer_care_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for CustomerCareAI"""
    return [
        create_tool_schema(
            name="get_tickets",
            description="Fetch support tickets with optional filtering by status and priority",
            properties={
                "status": string_prop("Filter by status: open, pending, solved, closed"),
                "priority": string_prop("Filter by priority: low, normal, high, urgent"),
                "max_results": integer_prop("Maximum tickets to return (default: 20)"),
            }
        ),
        create_tool_schema(
            name="get_ticket_by_id",
            description="Get detailed information about a specific ticket including conversation history",
            properties={
                "ticket_id": string_prop("The ticket ID to retrieve"),
            },
            required=["ticket_id"]
        ),
        create_tool_schema(
            name="answer_ticket",
            description="Post a response to a support ticket (public reply or internal note)",
            properties={
                "ticket_id": string_prop("The ticket ID to respond to"),
                "response": string_prop("The response message"),
                "internal_note": boolean_prop("If true, post as internal note (not visible to customer)"),
                "set_status": string_prop("Optionally change ticket status: open, pending, solved"),
            },
            required=["ticket_id", "response"]
        ),
        create_tool_schema(
            name="escalate_ticket",
            description="Escalate a ticket to a higher support tier",
            properties={
                "ticket_id": string_prop("The ticket ID to escalate"),
                "reason": string_prop("Reason for escalation"),
                "escalation_level": string_prop("Escalation level: tier2, tier3, manager, engineering"),
                "assign_to": string_prop("Optional: specific person to assign to"),
            },
            required=["ticket_id", "reason"]
        ),
        create_tool_schema(
            name="generate_response",
            description="Generate a suggested response based on ticket content and category",
            properties={
                "ticket_id": string_prop("The ticket ID to generate response for"),
                "response_type": string_prop("Response tone: helpful, apologetic, informative"),
                "include_kb_link": boolean_prop("Include link to help center"),
            },
            required=["ticket_id"]
        ),
        create_tool_schema(
            name="track_satisfaction",
            description="Get customer satisfaction metrics and trends",
            properties={
                "days_back": integer_prop("Number of days to analyze (default: 30)"),
            }
        ),
        create_tool_schema(
            name="get_pending_tickets",
            description="Get tickets that need attention, categorized by priority and age",
            properties={}
        ),
    ]
