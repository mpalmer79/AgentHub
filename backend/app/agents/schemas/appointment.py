from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, boolean_prop, array_string_prop


def get_appointment_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for AppointmentAI"""
    return [
        create_tool_schema(
            name="get_upcoming_events",
            description="Get upcoming calendar events for a specified number of days",
            properties={
                "days_ahead": integer_prop("Number of days to look ahead (default: 7)"),
                "max_results": integer_prop("Maximum number of events to return (default: 25)"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            }
        ),
        create_tool_schema(
            name="get_event_by_id",
            description="Get details of a specific calendar event",
            properties={
                "event_id": string_prop("The calendar event ID"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["event_id"]
        ),
        create_tool_schema(
            name="find_available_slots",
            description="Find available time slots for booking appointments",
            properties={
                "duration_minutes": integer_prop("Duration of the appointment in minutes (default: 60)"),
                "days_ahead": integer_prop("Number of days to search (default: 7)"),
                "working_hours_start": integer_prop("Start of working hours (default: 9)"),
                "working_hours_end": integer_prop("End of working hours (default: 17)"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            }
        ),
        create_tool_schema(
            name="book_appointment",
            description="Book a new appointment on the calendar",
            properties={
                "summary": string_prop("Title/name of the appointment"),
                "start_time": string_prop("Start time in ISO format (e.g., '2024-01-15T14:00:00Z')"),
                "end_time": string_prop("End time in ISO format"),
                "description": string_prop("Description or notes for the appointment"),
                "location": string_prop("Location or video meeting link"),
                "attendees": array_string_prop("List of attendee email addresses"),
                "send_notifications": boolean_prop("Whether to notify attendees (default: true)"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["summary", "start_time", "end_time"]
        ),
        create_tool_schema(
            name="reschedule_appointment",
            description="Reschedule an existing appointment to a new time",
            properties={
                "event_id": string_prop("The event ID to reschedule"),
                "new_start_time": string_prop("New start time in ISO format"),
                "new_end_time": string_prop("New end time in ISO format"),
                "notify_attendees": boolean_prop("Whether to notify attendees (default: true)"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["event_id", "new_start_time", "new_end_time"]
        ),
        create_tool_schema(
            name="cancel_appointment",
            description="Cancel an existing appointment",
            properties={
                "event_id": string_prop("The event ID to cancel"),
                "notify_attendees": boolean_prop("Whether to notify attendees (default: true)"),
                "cancellation_reason": string_prop("Reason for cancellation"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["event_id"]
        ),
        create_tool_schema(
            name="send_reminder",
            description="Send a reminder for an upcoming appointment",
            properties={
                "event_id": string_prop("The event ID to send reminder for"),
                "reminder_message": string_prop("Custom reminder message"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["event_id"]
        ),
        create_tool_schema(
            name="get_todays_schedule",
            description="Get today's complete schedule with upcoming and past events",
            properties={
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            }
        ),
        create_tool_schema(
            name="check_conflicts",
            description="Check if a proposed time slot has any scheduling conflicts",
            properties={
                "start_time": string_prop("Proposed start time in ISO format"),
                "end_time": string_prop("Proposed end time in ISO format"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["start_time", "end_time"]
        ),
        create_tool_schema(
            name="add_attendee",
            description="Add an attendee to an existing calendar event",
            properties={
                "event_id": string_prop("The event ID"),
                "attendee_email": string_prop("Email of the attendee to add"),
                "notify": boolean_prop("Whether to notify the new attendee (default: true)"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            },
            required=["event_id", "attendee_email"]
        ),
        create_tool_schema(
            name="get_no_show_risks",
            description="Identify appointments at risk of no-shows based on attendee responses and other factors",
            properties={
                "days_ahead": integer_prop("Number of days to analyze (default: 3)"),
                "calendar_id": string_prop("Calendar ID (default: 'primary')"),
            }
        ),
    ]
