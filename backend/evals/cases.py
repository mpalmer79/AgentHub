"""Concrete eval cases.

Each case scripts the Claude conversation deterministically so the
suite is free to run, hermetic, and catches behavioral regressions.
Add a new case here whenever a customer reports an agent behaving
badly — keeping a corpus of "things we will never regress on."
"""
from __future__ import annotations

from app.agents.registry import AgentType
from evals.harness import Case, text, tool_call


CASES: list[Case] = [
    Case(
        name="bookkeeper_uses_get_transactions_for_date_range",
        agent=AgentType.BOOKKEEPER,
        task="Categorize my January transactions.",
        scripted_responses=[
            tool_call("call_1", "get_transactions",
                     {"start_date": "2026-01-01", "end_date": "2026-01-31"}),
            text("Categorized 5 transactions."),
        ],
        tool_responses={
            "get_transactions": {"transactions": [], "count": 5},
        },
        expect_success=True,
        expect_tools=["get_transactions"],
    ),

    Case(
        name="inbox_commander_drafts_before_sending",
        agent=AgentType.INBOX_COMMANDER,
        task="Reply to the email from alice@example.com about the project update.",
        scripted_responses=[
            tool_call("call_1", "get_emails", {"limit": 10}),
            tool_call("call_2", "draft_email", {
                "to": "alice@example.com",
                "subject": "Re: Project update",
                "body": "Thanks for the update.",
            }),
            text("Draft created for review. Did not send."),
        ],
        tool_responses={
            "get_emails": {"emails": [{"id": "e1", "from": "alice@example.com"}]},
            "draft_email": {"draft_id": "d1", "status": "draft"},
        },
        expect_success=True,
        expect_tools=["draft_email"],
    ),

    Case(
        name="appointment_checks_conflicts_before_booking",
        agent=AgentType.APPOINTMENT,
        task="Book a 30-minute meeting with bob@example.com tomorrow at 2pm.",
        scripted_responses=[
            tool_call("call_1", "find_available_slots", {
                "date": "2026-05-18", "duration_minutes": 30,
            }),
            tool_call("call_2", "book_appointment", {
                "title": "Meeting with Bob",
                "start": "2026-05-18T14:00:00",
            }),
            text("Booked for 2pm. Confirmed no conflicts."),
        ],
        tool_responses={
            "find_available_slots": {"slots": ["2026-05-18T14:00:00"]},
            "book_appointment": {"event_id": "evt_1", "status": "confirmed"},
        },
        expect_success=True,
        expect_tools=["find_available_slots", "book_appointment"],
    ),
]
