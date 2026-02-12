from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, boolean_prop, array_string_prop


def get_compliance_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for ComplianceGuardAI"""
    return [
        create_tool_schema(
            name="monitor_regulations",
            description="Monitor regulatory changes and updates relevant to the business",
            properties={
                "industry": string_prop("Industry type: general, healthcare, finance, retail, technology"),
                "jurisdiction": string_prop("Jurisdiction: federal, state, local, international"),
                "categories": array_string_prop("Categories to monitor: privacy, tax, employment, safety, environmental"),
            }
        ),
        create_tool_schema(
            name="track_deadlines",
            description="Track compliance deadlines and upcoming requirements",
            properties={
                "days_ahead": integer_prop("Number of days to look ahead (default: 90)"),
                "include_completed": boolean_prop("Include completed deadlines (default: false)"),
            }
        ),
        create_tool_schema(
            name="audit_compliance",
            description="Audit current compliance status across different areas",
            properties={
                "area": string_prop("Area to audit: all, data_privacy, financial, employment, licensing"),
                "detailed": boolean_prop("Include detailed check results (default: true)"),
            }
        ),
        create_tool_schema(
            name="generate_policy",
            description="Generate a compliance policy document",
            properties={
                "policy_type": string_prop("Policy type: privacy, data_retention, acceptable_use, incident_response"),
                "company_name": string_prop("Company name to use in the policy"),
                "industry": string_prop("Industry for context: general, healthcare, finance, retail, technology"),
            },
            required=["policy_type"]
        ),
        create_tool_schema(
            name="prepare_audit_report",
            description="Prepare an audit-ready compliance report",
            properties={
                "report_type": string_prop("Report type: comprehensive, executive_summary, detailed"),
                "period_days": integer_prop("Period to cover in days (default: 90)"),
            }
        ),
    ]
