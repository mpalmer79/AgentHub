from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.core.database import get_supabase
from app.agents.tools.gmail import GmailTools
from app.agents.tools.calendar import GoogleCalendarTools


class HiringTools:
    """Tools for HireWellAI - recruiting and hiring automation"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.gmail = GmailTools(user_id)
        self.calendar = GoogleCalendarTools(user_id)
    
    async def get_candidate_emails(
        self,
        job_title: Optional[str] = None,
        days_back: int = 30,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Fetch emails related to job applications and candidates"""
        # Build search query for job-related emails
        q_parts = []
        
        # Common job application indicators
        q_parts.append("(resume OR cv OR application OR apply OR candidate OR position)")
        
        if job_title:
            q_parts.append(f'"{job_title}"')
        
        # Time filter
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        q_parts.append(f"after:{cutoff.strftime('%Y/%m/%d')}")
        
        query = " ".join(q_parts)
        
        result = await self.gmail.get_emails(
            query=query,
            max_results=max_results
        )
        
        if "error" in result:
            return result
        
        emails = result.get("emails", [])
        
        # Enrich with candidate-specific parsing
        candidates = []
        for email in emails:
            candidates.append({
                "email_id": email["id"],
                "from": email["from"],
                "subject": email["subject"],
                "date": email["date"],
                "snippet": email["snippet"][:200],
                "has_attachment": "attachment" in email.get("snippet", "").lower() or 
                                  "attached" in email.get("snippet", "").lower(),
                "is_unread": email.get("is_unread", False)
            })
        
        return {
            "candidate_emails": candidates,
            "count": len(candidates),
            "search_criteria": {
                "job_title": job_title,
                "days_back": days_back
            }
        }
    
    async def screen_resume(
        self,
        email_id: str,
        job_requirements: List[str],
        preferred_qualifications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Screen a candidate's resume/application against job requirements"""
        # Get the email with application
        email_result = await self.gmail.get_email_by_id(email_id)
        
        if "error" in email_result:
            return email_result
        
        email = email_result.get("email", {})
        body = email.get("body", "").lower()
        subject = email.get("subject", "")
        
        # Score against requirements
        required_matches = []
        required_missing = []
        
        for req in job_requirements:
            req_lower = req.lower()
            # Check for the requirement or common variations
            keywords = req_lower.split()
            if any(kw in body for kw in keywords):
                required_matches.append(req)
            else:
                required_missing.append(req)
        
        # Score against preferred qualifications
        preferred_matches = []
        if preferred_qualifications:
            for pref in preferred_qualifications:
                pref_lower = pref.lower()
                keywords = pref_lower.split()
                if any(kw in body for kw in keywords):
                    preferred_matches.append(pref)
        
        # Calculate scores
        required_score = (len(required_matches) / len(job_requirements)) * 100 if job_requirements else 0
        preferred_score = (len(preferred_matches) / len(preferred_qualifications)) * 100 if preferred_qualifications else 0
        overall_score = (required_score * 0.7) + (preferred_score * 0.3)
        
        # Determine recommendation
        if overall_score >= 70:
            recommendation = "strong_candidate"
            recommendation_text = "Recommend for interview"
        elif overall_score >= 50:
            recommendation = "potential_candidate"
            recommendation_text = "Consider for interview, review manually"
        else:
            recommendation = "not_recommended"
            recommendation_text = "Does not meet minimum requirements"
        
        # Store screening result
        supabase = get_supabase()
        screening_record = supabase.table("candidate_screenings").insert({
            "user_id": self.user_id,
            "email_id": email_id,
            "candidate_email": email.get("from"),
            "subject": subject,
            "required_matches": required_matches,
            "required_missing": required_missing,
            "preferred_matches": preferred_matches,
            "required_score": round(required_score, 1),
            "preferred_score": round(preferred_score, 1),
            "overall_score": round(overall_score, 1),
            "recommendation": recommendation,
            "screened_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "email_id": email_id,
            "candidate_email": email.get("from"),
            "subject": subject,
            "screening_results": {
                "required_matches": required_matches,
                "required_missing": required_missing,
                "preferred_matches": preferred_matches,
                "required_score": round(required_score, 1),
                "preferred_score": round(preferred_score, 1),
                "overall_score": round(overall_score, 1)
            },
            "recommendation": recommendation,
            "recommendation_text": recommendation_text,
            "screening_id": screening_record.data[0]["id"] if screening_record.data else None
        }
    
    async def schedule_interview(
        self,
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        duration_minutes: int = 60,
        interview_type: str = "phone_screen",
        interviewers: Optional[List[str]] = None,
        preferred_days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Schedule an interview with a candidate"""
        # Find available slots
        slots_result = await self.calendar.find_available_slots(
            duration_minutes=duration_minutes,
            days_ahead=preferred_days_ahead
        )
        
        if "error" in slots_result:
            return slots_result
        
        available_slots = slots_result.get("available_slots", [])
        
        if not available_slots:
            return {
                "error": "No available slots found",
                "message": f"No available {duration_minutes}-minute slots in the next {preferred_days_ahead} days"
            }
        
        # Pick the first available slot
        selected_slot = available_slots[0]
        
        # Format interview type for display
        interview_type_display = {
            "phone_screen": "Phone Screen",
            "technical": "Technical Interview",
            "behavioral": "Behavioral Interview",
            "final": "Final Interview",
            "panel": "Panel Interview"
        }.get(interview_type, interview_type.replace("_", " ").title())
        
        # Build attendee list
        attendees = [candidate_email]
        if interviewers:
            attendees.extend(interviewers)
        
        # Book the appointment
        booking_result = await self.calendar.book_appointment(
            summary=f"{interview_type_display}: {candidate_name} - {job_title}",
            start_time=selected_slot["start"],
            end_time=selected_slot["end"],
            description=f"Interview Type: {interview_type_display}\nCandidate: {candidate_name}\nPosition: {job_title}\n\nPlease be prepared with relevant questions for this {interview_type_display.lower()}.",
            attendees=attendees,
            send_notifications=True
        )
        
        if "error" in booking_result:
            return booking_result
        
        # Store in pipeline
        supabase = get_supabase()
        supabase.table("interview_schedule").insert({
            "user_id": self.user_id,
            "candidate_email": candidate_email,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "interview_type": interview_type,
            "event_id": booking_result.get("event_id"),
            "scheduled_time": selected_slot["start"],
            "duration_minutes": duration_minutes,
            "interviewers": interviewers,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "interview_scheduled",
            "candidate": {
                "name": candidate_name,
                "email": candidate_email
            },
            "interview": {
                "type": interview_type_display,
                "job_title": job_title,
                "date": selected_slot["start"],
                "duration_minutes": duration_minutes,
                "interviewers": interviewers
            },
            "event_id": booking_result.get("event_id"),
            "calendar_link": booking_result.get("html_link"),
            "message": f"Interview scheduled for {candidate_name} on {selected_slot['start']}"
        }
    
    async def send_status_update(
        self,
        candidate_email: str,
        candidate_name: str,
        status: str,
        job_title: str,
        custom_message: Optional[str] = None,
        next_steps: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a status update email to a candidate"""
        # Email templates based on status
        templates = {
            "application_received": {
                "subject": f"Application Received - {job_title}",
                "body": f"""Dear {candidate_name},

Thank you for applying for the {job_title} position. We have received your application and are currently reviewing it.

We appreciate your interest in joining our team. Our hiring team will carefully review your qualifications and experience.

{custom_message or ''}

{f'Next Steps: {next_steps}' if next_steps else 'We will be in touch within the next 1-2 weeks regarding next steps.'}

Best regards,
Hiring Team"""
            },
            "interview_scheduled": {
                "subject": f"Interview Scheduled - {job_title}",
                "body": f"""Dear {candidate_name},

Great news! We would like to invite you to interview for the {job_title} position.

{custom_message or 'Please check your calendar for the interview invitation with all the details.'}

{f'Next Steps: {next_steps}' if next_steps else 'Please confirm your attendance and let us know if you have any questions.'}

We look forward to speaking with you!

Best regards,
Hiring Team"""
            },
            "under_review": {
                "subject": f"Application Update - {job_title}",
                "body": f"""Dear {candidate_name},

Thank you for your patience. We wanted to let you know that your application for the {job_title} position is still under active review.

{custom_message or 'Our team is carefully evaluating all candidates to ensure the best fit for our organization.'}

{f'Next Steps: {next_steps}' if next_steps else 'We expect to have an update for you soon.'}

Thank you for your continued interest.

Best regards,
Hiring Team"""
            },
            "moved_forward": {
                "subject": f"Moving Forward - {job_title}",
                "body": f"""Dear {candidate_name},

We are pleased to inform you that you have been selected to move forward in our hiring process for the {job_title} position.

{custom_message or 'Your qualifications and experience have impressed our team.'}

{f'Next Steps: {next_steps}' if next_steps else 'We will be in touch shortly to schedule the next round.'}

Congratulations, and we look forward to the next steps!

Best regards,
Hiring Team"""
            },
            "rejection": {
                "subject": f"Application Update - {job_title}",
                "body": f"""Dear {candidate_name},

Thank you for taking the time to apply for the {job_title} position and for your interest in our company.

After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.

{custom_message or 'We encourage you to apply for future openings that match your skills and experience.'}

We wish you the best in your job search and future endeavors.

Best regards,
Hiring Team"""
            }
        }
        
        template = templates.get(status)
        if not template:
            return {"error": f"Unknown status: {status}. Valid statuses: {list(templates.keys())}"}
        
        # Send the email
        send_result = await self.gmail.send_email(
            to=candidate_email,
            subject=template["subject"],
            body=template["body"]
        )
        
        if "error" in send_result:
            return send_result
        
        # Track the communication
        supabase = get_supabase()
        supabase.table("candidate_communications").insert({
            "user_id": self.user_id,
            "candidate_email": candidate_email,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "status": status,
            "subject": template["subject"],
            "message_id": send_result.get("message_id"),
            "sent_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "email_sent",
            "candidate": {
                "name": candidate_name,
                "email": candidate_email
            },
            "update_type": status,
            "job_title": job_title,
            "subject": template["subject"],
            "message_id": send_result.get("message_id"),
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def get_pipeline_status(
        self,
        job_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get overview of the hiring pipeline status"""
        supabase = get_supabase()
        
        # Get all screenings
        screenings_query = supabase.table("candidate_screenings") \
            .select("*") \
            .eq("user_id", self.user_id)
        
        if job_title:
            screenings_query = screenings_query.ilike("subject", f"%{job_title}%")
        
        screenings = screenings_query.execute()
        
        # Get all scheduled interviews
        interviews_query = supabase.table("interview_schedule") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("status", "scheduled")
        
        if job_title:
            interviews_query = interviews_query.eq("job_title", job_title)
        
        interviews = interviews_query.execute()
        
        # Get recent communications
        comms_query = supabase.table("candidate_communications") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .order("sent_at", desc=True) \
            .limit(50)
        
        if job_title:
            comms_query = comms_query.eq("job_title", job_title)
        
        communications = comms_query.execute()
        
        # Analyze pipeline
        screenings_data = screenings.data or []
        interviews_data = interviews.data or []
        comms_data = communications.data or []
        
        # Categorize candidates
        strong_candidates = [s for s in screenings_data if s.get("overall_score", 0) >= 70]
        potential_candidates = [s for s in screenings_data if 50 <= s.get("overall_score", 0) < 70]
        not_qualified = [s for s in screenings_data if s.get("overall_score", 0) < 50]
        
        # Track statuses from communications
        status_counts = {}
        for comm in comms_data:
            status = comm.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "pipeline_summary": {
                "total_screened": len(screenings_data),
                "strong_candidates": len(strong_candidates),
                "potential_candidates": len(potential_candidates),
                "not_qualified": len(not_qualified),
                "interviews_scheduled": len(interviews_data)
            },
            "strong_candidates": [
                {
                    "email": s.get("candidate_email"),
                    "score": s.get("overall_score"),
                    "screened_at": s.get("screened_at")
                }
                for s in strong_candidates[:10]
            ],
            "upcoming_interviews": [
                {
                    "candidate_name": i.get("candidate_name"),
                    "candidate_email": i.get("candidate_email"),
                    "interview_type": i.get("interview_type"),
                    "scheduled_time": i.get("scheduled_time")
                }
                for i in interviews_data[:10]
            ],
            "status_distribution": status_counts,
            "filter": {
                "job_title": job_title
            }
        }
    
    async def coordinate_reference_check(
        self,
        candidate_name: str,
        candidate_email: str,
        reference_email: str,
        reference_name: str,
        job_title: str
    ) -> Dict[str, Any]:
        """Send a reference check request email"""
        subject = f"Reference Request for {candidate_name} - {job_title} Position"
        
        body = f"""Dear {reference_name},

{candidate_name} has applied for the {job_title} position at our company and has listed you as a professional reference.

We would greatly appreciate if you could take a few minutes to answer the following questions about your experience working with {candidate_name}:

1. In what capacity did you work with {candidate_name}, and for how long?

2. What were {candidate_name}'s primary responsibilities?

3. How would you describe their work quality and reliability?

4. What are their greatest strengths?

5. Are there any areas where they could improve?

6. Would you work with {candidate_name} again if given the opportunity?

7. Is there anything else you'd like to share about {candidate_name}?

Your feedback will be kept confidential and will only be used as part of our hiring process.

Please reply to this email with your responses at your earliest convenience.

Thank you for your time and assistance.

Best regards,
Hiring Team"""
        
        # Send the reference request
        send_result = await self.gmail.send_email(
            to=reference_email,
            subject=subject,
            body=body
        )
        
        if "error" in send_result:
            return send_result
        
        # Track the reference check
        supabase = get_supabase()
        supabase.table("reference_checks").insert({
            "user_id": self.user_id,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "reference_name": reference_name,
            "reference_email": reference_email,
            "job_title": job_title,
            "message_id": send_result.get("message_id"),
            "status": "requested",
            "requested_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "reference_request_sent",
            "candidate": {
                "name": candidate_name,
                "email": candidate_email
            },
            "reference": {
                "name": reference_name,
                "email": reference_email
            },
            "job_title": job_title,
            "message_id": send_result.get("message_id")
        }
    
    async def get_candidates_needing_followup(
        self,
        days_without_contact: int = 7
    ) -> Dict[str, Any]:
        """Identify candidates who haven't been contacted recently"""
        supabase = get_supabase()
        
        cutoff = datetime.utcnow() - timedelta(days=days_without_contact)
        
        # Get all candidates from screenings
        screenings = supabase.table("candidate_screenings") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("overall_score", 50) \
            .execute()
        
        # Get recent communications
        communications = supabase.table("candidate_communications") \
            .select("candidate_email, sent_at") \
            .eq("user_id", self.user_id) \
            .gte("sent_at", cutoff.isoformat()) \
            .execute()
        
        recently_contacted = set(c["candidate_email"] for c in (communications.data or []))
        
        needs_followup = []
        for screening in (screenings.data or []):
            candidate_email = screening.get("candidate_email")
            if candidate_email and candidate_email not in recently_contacted:
                screened_at = screening.get("screened_at")
                days_since = None
                if screened_at:
                    try:
                        screened_date = datetime.fromisoformat(screened_at.replace("Z", "+00:00"))
                        days_since = (datetime.utcnow().replace(tzinfo=screened_date.tzinfo) - screened_date).days
                    except (ValueError, TypeError):
                        pass
                
                needs_followup.append({
                    "candidate_email": candidate_email,
                    "subject": screening.get("subject"),
                    "overall_score": screening.get("overall_score"),
                    "screened_at": screened_at,
                    "days_since_screening": days_since
                })
        
        return {
            "candidates_needing_followup": needs_followup,
            "count": len(needs_followup),
            "criteria": {
                "days_without_contact": days_without_contact,
                "minimum_score": 50
            }
        }
