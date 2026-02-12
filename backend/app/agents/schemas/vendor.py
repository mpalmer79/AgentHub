from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, number_prop


def get_vendor_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for VendorNegotiatorAI"""
    return [
        create_tool_schema(
            name="analyze_contracts",
            description="Analyze vendor contracts and extract key terms, costs, and renewal dates",
            properties={
                "vendor_name": string_prop("Filter by vendor name (partial match)"),
                "category": string_prop("Filter by category: software, services, supplies, logistics"),
                "expiring_within_days": integer_prop("Only show contracts expiring within N days"),
            }
        ),
        create_tool_schema(
            name="benchmark_pricing",
            description="Benchmark vendor pricing against market rates to identify if you're overpaying",
            properties={
                "vendor_name": string_prop("Name of the vendor"),
                "category": string_prop("Category: software, services, supplies, logistics"),
                "current_price": number_prop("Current monthly price being paid"),
                "service_description": string_prop("Description of the service for better matching"),
            },
            required=["vendor_name", "category", "current_price"]
        ),
        create_tool_schema(
            name="identify_savings",
            description="Identify savings opportunities across all vendor relationships",
            properties={
                "min_savings_threshold": number_prop("Minimum annual savings to include (default: 100)"),
            }
        ),
        create_tool_schema(
            name="draft_negotiation",
            description="Draft a negotiation email or script for vendor discussions",
            properties={
                "vendor_name": string_prop("Name of the vendor"),
                "negotiation_type": string_prop("Type: renewal, price_reduction, service_upgrade, cancellation_prevention"),
                "current_terms": string_prop("Summary of current contract terms"),
                "desired_outcome": string_prop("What you want to achieve"),
                "tone": string_prop("Tone: professional, firm, or friendly (default: professional)"),
            },
            required=["vendor_name", "negotiation_type", "current_terms", "desired_outcome"]
        ),
        create_tool_schema(
            name="track_renewals",
            description="Track upcoming contract renewals and required actions",
            properties={
                "days_ahead": integer_prop("Number of days to look ahead (default: 90)"),
            }
        ),
    ]
