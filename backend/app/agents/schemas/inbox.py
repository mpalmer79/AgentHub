from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, boolean_prop


def get_inbox_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for InboxCommanderAI"""
    return [
        create_tool_schema(
            name="get_emails",
            description="Fetch emails from Gmail inbox with optional filtering by query, label, or unread status",
            properties={
                "query": string_prop("Gmail search query (e.g., 'from:boss@company.com', 'subject:urgent')"),
                "label": string_prop("Filter by label (e.g., 'INBOX', 'IMPORTANT', 'STARRED')"),
                "max_results": integer_prop("Maximum number of emails to return (default: 20, max: 50)"),
                "unread_only": boolean_prop("Only return unread emails"),
            }
        ),
        create_tool_schema(
            name="get_email_by_id",
            description="Get the full content of a specific email by its ID",
            properties={
                "email_id": string_prop("The Gmail message ID"),
            },
            required=["email_id"]
        ),
        create_tool_schema(
            name="triage_inbox",
            description="Analyze and categorize recent emails into Urgent, Needs Response, Informational, and Low Priority",
            properties={
                "time_window_hours": integer_prop("How many hours back to analyze (default: 24)"),
            }
        ),
        create_tool_schema(
            name="draft_response",
            description="Create a draft reply to an email. The draft will be saved for user review before sending.",
            properties={
                "email_id": string_prop("The ID of the email to reply to"),
                "response_body": string_prop("The body text of the reply"),
                "include_original": boolean_prop("Include the original email in the reply (default: true)"),
            },
            required=["email_id", "response_body"]
        ),
        create_tool_schema(
            name="send_email",
            description="Send a new email or reply. Use with caution - prefer draft_response for replies.",
            properties={
                "to": string_prop("Recipient email address"),
                "subject": string_prop("Email subject line"),
                "body": string_prop("Email body text"),
                "cc": string_prop("CC recipients (comma-separated)"),
                "reply_to_id": string_prop("Optional: ID of email this is replying to"),
            },
            required=["to", "subject", "body"]
        ),
        create_tool_schema(
            name="schedule_followup",
            description="Schedule a follow-up reminder for an email",
            properties={
                "email_id": string_prop("The email ID to follow up on"),
                "followup_date": string_prop("Date for follow-up in YYYY-MM-DD format"),
                "followup_note": string_prop("Note about what to follow up on"),
            },
            required=["email_id", "followup_date", "followup_note"]
        ),
        create_tool_schema(
            name="extract_action_items",
            description="Extract action items and tasks from an email's content",
            properties={
                "email_id": string_prop("The email ID to analyze for action items"),
            },
            required=["email_id"]
        ),
        create_tool_schema(
            name="apply_label",
            description="Apply a label to an email for organization",
            properties={
                "email_id": string_prop("The email ID to label"),
                "label_name": string_prop("Label name to apply (will be created if doesn't exist)"),
            },
            required=["email_id", "label_name"]
        ),
        create_tool_schema(
            name="mark_as_read",
            description="Mark an email as read",
            properties={
                "email_id": string_prop("The email ID to mark as read"),
            },
            required=["email_id"]
        ),
        create_tool_schema(
            name="archive_email",
            description="Archive an email (remove from inbox but keep in All Mail)",
            properties={
                "email_id": string_prop("The email ID to archive"),
            },
            required=["email_id"]
        ),
        create_tool_schema(
            name="get_followups_due",
            description="Get list of scheduled follow-ups that are due today or overdue",
            properties={}
        ),
    ]
