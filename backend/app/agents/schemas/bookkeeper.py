from typing import List, Dict, Any
from .base import create_tool_schema, string_prop


def get_bookkeeper_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for BookkeeperAI"""
    return [
        create_tool_schema(
            name="get_transactions",
            description="Fetch transactions from QuickBooks within a date range",
            properties={
                "start_date": string_prop("Start date in YYYY-MM-DD format"),
                "end_date": string_prop("End date in YYYY-MM-DD format"),
                "account_id": string_prop("Optional: Filter by specific account ID"),
            },
            required=["start_date", "end_date"]
        ),
        create_tool_schema(
            name="categorize_transaction",
            description="Categorize a transaction in QuickBooks",
            properties={
                "transaction_id": string_prop("The transaction ID to categorize"),
                "category": string_prop("The category/account to assign"),
                "memo": string_prop("Optional memo for the categorization"),
            },
            required=["transaction_id", "category"]
        ),
        create_tool_schema(
            name="get_accounts",
            description="Get list of accounts from QuickBooks",
            properties={
                "account_type": string_prop("Optional: Filter by account type"),
            }
        ),
        create_tool_schema(
            name="get_account_balance",
            description="Get the balance of a specific account",
            properties={
                "account_id": string_prop("The account ID to check"),
            },
            required=["account_id"]
        ),
        create_tool_schema(
            name="create_expense_report",
            description="Generate an expense report for a date range",
            properties={
                "start_date": string_prop("Start date in YYYY-MM-DD format"),
                "end_date": string_prop("End date in YYYY-MM-DD format"),
                "group_by": string_prop("Group by: 'category', 'vendor', 'month'"),
            },
            required=["start_date", "end_date"]
        ),
        create_tool_schema(
            name="flag_for_review",
            description="Flag a transaction for human review",
            properties={
                "transaction_id": string_prop("The transaction ID to flag"),
                "reason": string_prop("Reason for flagging"),
                "suggested_action": string_prop("Suggested action for the reviewer"),
            },
            required=["transaction_id", "reason"]
        ),
    ]
