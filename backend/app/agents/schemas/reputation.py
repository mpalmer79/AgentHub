from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, array_string_prop


def get_reputation_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for ReputationShieldAI"""
    return [
        create_tool_schema(
            name="monitor_reviews",
            description="Monitor reviews across connected platforms",
            properties={
                "platforms": array_string_prop("Platforms to monitor (google, yelp, facebook)"),
                "days_back": integer_prop("Days to look back (default: 30)"),
                "min_rating": integer_prop("Filter by maximum rating (to find negative reviews)"),
            }
        ),
        create_tool_schema(
            name="draft_response",
            description="Draft a response to a review",
            properties={
                "review_id": string_prop("The review ID to respond to"),
                "review_text": string_prop("The review text content"),
                "rating": integer_prop("The review rating (1-5)"),
                "reviewer_name": string_prop("Name of the reviewer"),
                "response_tone": string_prop("Tone: professional or casual (default: professional)"),
            },
            required=["review_id", "review_text", "rating", "reviewer_name"]
        ),
        create_tool_schema(
            name="request_reviews",
            description="Generate review request emails for customers",
            properties={
                "customer_emails": array_string_prop("List of customer email addresses"),
                "customer_names": array_string_prop("List of customer names (same order as emails)"),
                "platform": string_prop("Platform to request review on (google, yelp, facebook)"),
                "custom_message": string_prop("Custom message template (use {name} and {platform} placeholders)"),
            },
            required=["customer_emails", "customer_names"]
        ),
        create_tool_schema(
            name="analyze_sentiment",
            description="Analyze review sentiment trends over time",
            properties={
                "time_period_days": integer_prop("Number of days to analyze (default: 90)"),
            }
        ),
        create_tool_schema(
            name="track_competitors",
            description="Set up tracking for competitor businesses",
            properties={
                "competitor_names": array_string_prop("Names of competitor businesses to track"),
            },
            required=["competitor_names"]
        ),
        create_tool_schema(
            name="get_crisis_alerts",
            description="Check for reputation crisis indicators and urgent alerts",
            properties={}
        ),
    ]
