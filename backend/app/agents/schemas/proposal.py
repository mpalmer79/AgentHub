from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, number_prop, boolean_prop, array_string_prop


def get_proposal_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for ProposalProAI"""
    return [
        create_tool_schema(
            name="generate_proposal",
            description="Generate a customized proposal for a client project",
            properties={
                "client_name": string_prop("Name of the client/company"),
                "project_title": string_prop("Title of the project"),
                "project_description": string_prop("Description of what the project entails"),
                "services": array_string_prop("List of services/deliverables to include"),
                "estimated_value": number_prop("Estimated project value in dollars"),
                "timeline_weeks": integer_prop("Estimated timeline in weeks"),
                "template": string_prop("Template type: standard, detailed, or brief"),
            },
            required=["client_name", "project_title", "project_description", "services"]
        ),
        create_tool_schema(
            name="respond_to_rfp",
            description="Generate a comprehensive response to an RFP (Request for Proposal)",
            properties={
                "rfp_title": string_prop("Title of the RFP"),
                "client_name": string_prop("Name of the issuing organization"),
                "requirements": array_string_prop("List of RFP requirements to address"),
                "deadline": string_prop("RFP submission deadline (YYYY-MM-DD)"),
                "budget_range": string_prop("Client's stated budget range if known"),
                "evaluation_criteria": array_string_prop("Evaluation criteria mentioned in RFP"),
            },
            required=["rfp_title", "client_name", "requirements", "deadline"]
        ),
        create_tool_schema(
            name="price_project",
            description="Generate intelligent pricing for a project based on scope and complexity",
            properties={
                "project_type": string_prop("Type: consulting, development, design, marketing, implementation, training, support, strategy"),
                "scope_items": array_string_prop("List of scope items/deliverables to price"),
                "complexity": string_prop("Complexity level: low, medium, high, very_high"),
                "timeline_preference": string_prop("Timeline: rushed, accelerated, standard, flexible"),
                "include_options": boolean_prop("Include tiered pricing options (default: true)"),
            },
            required=["project_type", "scope_items"]
        ),
        create_tool_schema(
            name="track_proposal",
            description="Track proposal status and deal pipeline progress",
            properties={
                "proposal_id": string_prop("Specific proposal ID to track (optional)"),
                "status_filter": string_prop("Filter by status: draft, sent, negotiating, won, lost"),
                "days_back": integer_prop("Number of days to look back (default: 90)"),
            }
        ),
        create_tool_schema(
            name="analyze_win_rate",
            description="Analyze win/loss patterns to improve proposal success rate",
            properties={
                "period_days": integer_prop("Analysis period in days (default: 180)"),
            }
        ),
    ]
