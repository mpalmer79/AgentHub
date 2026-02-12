from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, number_prop, boolean_prop


def get_cashflow_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for CashFlowCommanderAI"""
    return [
        create_tool_schema(
            name="project_cashflow",
            description="Project cash flow for the next N days based on historical patterns",
            properties={
                "days_ahead": integer_prop("Number of days to project (default: 90)"),
                "include_recurring": boolean_prop("Include recurring transactions (default: true)"),
            }
        ),
        create_tool_schema(
            name="prioritize_collections",
            description="Analyze and prioritize accounts receivable for collection",
            properties={
                "min_amount": number_prop("Minimum amount to include (default: 100)"),
                "days_overdue_threshold": integer_prop("Days overdue threshold (default: 30)"),
            }
        ),
        create_tool_schema(
            name="optimize_payments",
            description="Optimize payment timing to maximize cash position",
            properties={
                "available_cash": number_prop("Available cash for payments (auto-detected if not provided)"),
            }
        ),
        create_tool_schema(
            name="send_invoice_reminder",
            description="Generate a payment reminder for an overdue invoice",
            properties={
                "customer_name": string_prop("Customer name"),
                "customer_email": string_prop("Customer email address"),
                "invoice_number": string_prop("Invoice number"),
                "amount": number_prop("Amount due"),
                "days_overdue": integer_prop("Number of days overdue"),
            },
            required=["customer_name", "customer_email", "invoice_number", "amount", "days_overdue"]
        ),
        create_tool_schema(
            name="score_customer_risk",
            description="Assess payment risk score for a customer based on history",
            properties={
                "customer_name": string_prop("Customer name to analyze"),
            },
            required=["customer_name"]
        ),
        create_tool_schema(
            name="get_cash_alerts",
            description="Get current cash flow alerts and warnings",
            properties={}
        ),
    ]
