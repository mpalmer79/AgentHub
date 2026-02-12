from typing import List, Dict, Any
from .base import create_tool_schema, string_prop, integer_prop, array_string_prop


def get_hiring_schema() -> List[Dict[str, Any]]:
    """Return tool schemas for HireWellAI"""
    return [
        create_tool_schema(
            name="get_candidate_emails",
            description="Fetch emails related to job applications and candidates",
            properties={
                "job_title": string_prop("Filter by job title/position"),
                "days_back": integer_prop("Number of days to look back (default: 30)"),
                "max_results": integer_prop("Maximum results to return (default: 50)"),
            }
        ),
        create_tool_schema(
            name="screen_resume",
            description="Screen a candidate's resume/application against job requirements",
            properties={
                "email_id": string_prop("The email ID containing the application"),
                "job_requirements": array_string_prop("List of required qualifications"),
                "preferred_qualifications": array_string_prop("List of preferred qualifications"),
            },
            required=["email_id", "job_requirements"]
        ),
        create_tool_schema(
            name="schedule_interview",
            description="Schedule an interview with a candidate",
            properties={
                "candidate_email": string_prop("Candidate's email address"),
                "candidate_name": string_prop("Candidate's full name"),
                "job_title": string_prop("Position being interviewed for"),
                "duration_minutes": integer_prop("Interview duration (default: 60)"),
                "interview_type": string_prop("Type: phone_screen, technical, behavioral, final, panel"),
                "interviewers": array_string_prop("List of interviewer email addresses"),
                "preferred_days_ahead": integer_prop("Days to search for slots (default: 7)"),
            },
            required=["candidate_email", "candidate_name", "job_title"]
        ),
        create_tool_schema(
            name="send_status_update",
            description="Send a status update email to a candidate",
            properties={
                "candidate_email": string_prop("Candidate's email address"),
                "candidate_name": string_prop("Candidate's full name"),
                "status": string_prop("Status: application_received, interview_scheduled, under_review, moved_forward, rejection"),
                "job_title": string_prop("Position title"),
                "custom_message": string_prop("Optional custom message to include"),
                "next_steps": string_prop("Optional next steps information"),
            },
            required=["candidate_email", "candidate_name", "status", "job_title"]
        ),
        create_tool_schema(
            name="get_pipeline_status",
            description="Get overview of the hiring pipeline status",
            properties={
                "job_title": string_prop("Filter by specific job title"),
            }
        ),
        create_tool_schema(
            name="coordinate_reference_check",
            description="Send a reference check request email",
            properties={
                "candidate_name": string_prop("Candidate's full name"),
                "candidate_email": string_prop("Candidate's email"),
                "reference_email": string_prop("Reference person's email"),
                "reference_name": string_prop("Reference person's name"),
                "job_title": string_prop("Position title"),
            },
            required=["candidate_name", "candidate_email", "reference_email", "reference_name", "job_title"]
        ),
        create_tool_schema(
            name="get_candidates_needing_followup",
            description="Identify candidates who haven't been contacted recently",
            properties={
                "days_without_contact": integer_prop("Days threshold (default: 7)"),
            }
        ),
    ]
