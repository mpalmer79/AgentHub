from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx

from app.core.database import get_supabase


class GoogleCalendarTools:
    """Tools for interacting with Google Calendar API"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._client_info = None
    
    async def _get_client(self) -> Dict[str, str]:
        """Get authenticated Google Calendar client info"""
        if not self._client_info:
            from app.api.integrations import get_google_calendar_client
            self._client_info = await get_google_calendar_client(self.user_id)
        return self._client_info
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Google Calendar API"""
        client_info = await self._get_client()
        base_url = "https://www.googleapis.com/calendar/v3"
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {client_info['access_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code in (200, 201, 204):
            if response.text:
                return response.json()
            return {"success": True}
        else:
            return {
                "error": f"Google Calendar API error: {response.status_code}",
                "details": response.text
            }
    
    def _parse_event(self, event: Dict) -> Dict[str, Any]:
        """Parse Calendar event into structured format"""
        start = event.get("start", {})
        end = event.get("end", {})
        
        return {
            "id": event.get("id"),
            "summary": event.get("summary", "No Title"),
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "start": start.get("dateTime") or start.get("date"),
            "end": end.get("dateTime") or end.get("date"),
            "is_all_day": "date" in start and "dateTime" not in start,
            "attendees": [
                {
                    "email": a.get("email"),
                    "name": a.get("displayName", ""),
                    "response": a.get("responseStatus", "needsAction"),
                    "organizer": a.get("organizer", False)
                }
                for a in event.get("attendees", [])
            ],
            "organizer": event.get("organizer", {}).get("email"),
            "status": event.get("status"),
            "html_link": event.get("htmlLink"),
            "created": event.get("created"),
            "updated": event.get("updated"),
            "recurring": "recurringEventId" in event,
            "conference_data": event.get("conferenceData"),
            "reminders": event.get("reminders", {})
        }
    
    async def get_upcoming_events(
        self,
        days_ahead: int = 7,
        max_results: int = 25,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Get upcoming calendar events"""
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"
        
        result = await self._make_request(
            "GET",
            f"calendars/{calendar_id}/events",
            params={
                "timeMin": time_min,
                "timeMax": time_max,
                "maxResults": max_results,
                "singleEvents": "true",
                "orderBy": "startTime"
            }
        )
        
        if "error" in result:
            return result
        
        events = [self._parse_event(e) for e in result.get("items", [])]
        
        return {
            "events": events,
            "count": len(events),
            "time_range": {
                "start": time_min,
                "end": time_max,
                "days": days_ahead
            }
        }
    
    async def get_event_by_id(
        self,
        event_id: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Get a specific calendar event by ID"""
        result = await self._make_request(
            "GET",
            f"calendars/{calendar_id}/events/{event_id}"
        )
        
        if "error" in result:
            return result
        
        return {"event": self._parse_event(result)}
    
    async def find_available_slots(
        self,
        duration_minutes: int = 60,
        days_ahead: int = 7,
        working_hours_start: int = 9,
        working_hours_end: int = 17,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Find available time slots in the calendar"""
        events_result = await self.get_upcoming_events(
            days_ahead=days_ahead,
            max_results=100,
            calendar_id=calendar_id
        )
        
        if "error" in events_result:
            return events_result
        
        events = events_result.get("events", [])
        
        # Build list of busy periods
        busy_periods = []
        for event in events:
            if event.get("is_all_day"):
                continue
            start_str = event.get("start")
            end_str = event.get("end")
            if start_str and end_str:
                try:
                    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                    busy_periods.append((start, end))
                except ValueError:
                    continue
        
        busy_periods.sort(key=lambda x: x[0])
        
        # Find available slots
        available_slots = []
        now = datetime.utcnow()
        current_date = now.date()
        
        for day_offset in range(days_ahead):
            check_date = current_date + timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
            
            day_start = datetime(
                check_date.year, check_date.month, check_date.day,
                working_hours_start, 0, 0
            )
            day_end = datetime(
                check_date.year, check_date.month, check_date.day,
                working_hours_end, 0, 0
            )
            
            # Start from now if it's today
            if day_offset == 0 and now > day_start:
                day_start = now + timedelta(minutes=30 - now.minute % 30)
            
            current_time = day_start
            
            while current_time + timedelta(minutes=duration_minutes) <= day_end:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with any busy period
                is_available = True
                for busy_start, busy_end in busy_periods:
                    if current_time < busy_end and slot_end > busy_start:
                        is_available = False
                        current_time = busy_end
                        break
                
                if is_available:
                    available_slots.append({
                        "start": current_time.isoformat(),
                        "end": slot_end.isoformat(),
                        "duration_minutes": duration_minutes
                    })
                    current_time = slot_end
                
                if len(available_slots) >= 10:
                    break
            
            if len(available_slots) >= 10:
                break
        
        return {
            "available_slots": available_slots,
            "count": len(available_slots),
            "parameters": {
                "duration_minutes": duration_minutes,
                "days_ahead": days_ahead,
                "working_hours": f"{working_hours_start}:00-{working_hours_end}:00"
            }
        }
    
    async def book_appointment(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        send_notifications: bool = True,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Book a new appointment/event"""
        event_data = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
        }
        
        if description:
            event_data["description"] = description
        
        if location:
            event_data["location"] = location
        
        if attendees:
            event_data["attendees"] = [{"email": email} for email in attendees]
        
        result = await self._make_request(
            "POST",
            f"calendars/{calendar_id}/events",
            params={"sendNotifications": str(send_notifications).lower()},
            data=event_data
        )
        
        if "error" in result:
            return result
        
        # Store in database for tracking
        supabase = get_supabase()
        supabase.table("scheduled_appointments").insert({
            "user_id": self.user_id,
            "event_id": result.get("id"),
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees or [],
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "booked",
            "event": self._parse_event(result),
            "message": f"Appointment '{summary}' has been scheduled"
        }
    
    async def reschedule_appointment(
        self,
        event_id: str,
        new_start_time: str,
        new_end_time: str,
        notify_attendees: bool = True,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Reschedule an existing appointment"""
        # First get the existing event
        existing = await self.get_event_by_id(event_id, calendar_id)
        
        if "error" in existing:
            return existing
        
        event = existing.get("event", {})
        
        update_data = {
            "start": {"dateTime": new_start_time, "timeZone": "UTC"},
            "end": {"dateTime": new_end_time, "timeZone": "UTC"}
        }
        
        result = await self._make_request(
            "PATCH",
            f"calendars/{calendar_id}/events/{event_id}",
            params={"sendNotifications": str(notify_attendees).lower()},
            data=update_data
        )
        
        if "error" in result:
            return result
        
        # Update database record
        supabase = get_supabase()
        supabase.table("scheduled_appointments") \
            .update({
                "start_time": new_start_time,
                "end_time": new_end_time,
                "status": "rescheduled",
                "rescheduled_at": datetime.utcnow().isoformat()
            }) \
            .eq("event_id", event_id) \
            .eq("user_id", self.user_id) \
            .execute()
        
        return {
            "status": "rescheduled",
            "event": self._parse_event(result),
            "previous_time": {
                "start": event.get("start"),
                "end": event.get("end")
            },
            "new_time": {
                "start": new_start_time,
                "end": new_end_time
            },
            "message": f"Appointment has been rescheduled"
        }
    
    async def cancel_appointment(
        self,
        event_id: str,
        notify_attendees: bool = True,
        cancellation_reason: Optional[str] = None,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Cancel an appointment"""
        # Get event details first
        existing = await self.get_event_by_id(event_id, calendar_id)
        
        if "error" in existing:
            return existing
        
        event = existing.get("event", {})
        
        result = await self._make_request(
            "DELETE",
            f"calendars/{calendar_id}/events/{event_id}",
            params={"sendNotifications": str(notify_attendees).lower()}
        )
        
        if "error" in result:
            return result
        
        # Update database record
        supabase = get_supabase()
        supabase.table("scheduled_appointments") \
            .update({
                "status": "cancelled",
                "cancellation_reason": cancellation_reason,
                "cancelled_at": datetime.utcnow().isoformat()
            }) \
            .eq("event_id", event_id) \
            .eq("user_id", self.user_id) \
            .execute()
        
        return {
            "status": "cancelled",
            "event_id": event_id,
            "summary": event.get("summary"),
            "message": f"Appointment '{event.get('summary')}' has been cancelled"
        }
    
    async def send_reminder(
        self,
        event_id: str,
        reminder_message: Optional[str] = None,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Send a reminder for an upcoming appointment"""
        existing = await self.get_event_by_id(event_id, calendar_id)
        
        if "error" in existing:
            return existing
        
        event = existing.get("event", {})
        
        # Store reminder in database
        supabase = get_supabase()
        supabase.table("appointment_reminders").insert({
            "user_id": self.user_id,
            "event_id": event_id,
            "summary": event.get("summary"),
            "start_time": event.get("start"),
            "attendees": [a.get("email") for a in event.get("attendees", [])],
            "reminder_message": reminder_message,
            "sent_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "reminder_sent",
            "event_id": event_id,
            "summary": event.get("summary"),
            "start_time": event.get("start"),
            "attendees_notified": len(event.get("attendees", [])),
            "message": reminder_message or f"Reminder sent for '{event.get('summary')}'"
        }
    
    async def get_todays_schedule(
        self,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Get today's complete schedule"""
        now = datetime.utcnow()
        start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
        end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
        
        result = await self._make_request(
            "GET",
            f"calendars/{calendar_id}/events",
            params={
                "timeMin": start_of_day.isoformat() + "Z",
                "timeMax": end_of_day.isoformat() + "Z",
                "singleEvents": "true",
                "orderBy": "startTime"
            }
        )
        
        if "error" in result:
            return result
        
        events = [self._parse_event(e) for e in result.get("items", [])]
        
        # Categorize events
        upcoming = []
        past = []
        for event in events:
            start_str = event.get("start")
            if start_str:
                try:
                    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    if start.replace(tzinfo=None) > now:
                        upcoming.append(event)
                    else:
                        past.append(event)
                except ValueError:
                    upcoming.append(event)
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "total_events": len(events),
            "upcoming": upcoming,
            "past": past,
            "next_event": upcoming[0] if upcoming else None
        }
    
    async def check_conflicts(
        self,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Check if a proposed time slot has any conflicts"""
        result = await self._make_request(
            "GET",
            f"calendars/{calendar_id}/events",
            params={
                "timeMin": start_time,
                "timeMax": end_time,
                "singleEvents": "true"
            }
        )
        
        if "error" in result:
            return result
        
        conflicts = [self._parse_event(e) for e in result.get("items", [])]
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "proposed_slot": {
                "start": start_time,
                "end": end_time
            }
        }
    
    async def add_attendee(
        self,
        event_id: str,
        attendee_email: str,
        notify: bool = True,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Add an attendee to an existing event"""
        existing = await self.get_event_by_id(event_id, calendar_id)
        
        if "error" in existing:
            return existing
        
        event = existing.get("event", {})
        current_attendees = event.get("attendees", [])
        
        # Check if already attending
        for attendee in current_attendees:
            if attendee.get("email", "").lower() == attendee_email.lower():
                return {
                    "status": "already_added",
                    "message": f"{attendee_email} is already an attendee"
                }
        
        new_attendees = [{"email": a.get("email")} for a in current_attendees]
        new_attendees.append({"email": attendee_email})
        
        result = await self._make_request(
            "PATCH",
            f"calendars/{calendar_id}/events/{event_id}",
            params={"sendNotifications": str(notify).lower()},
            data={"attendees": new_attendees}
        )
        
        if "error" in result:
            return result
        
        return {
            "status": "attendee_added",
            "event_id": event_id,
            "attendee": attendee_email,
            "total_attendees": len(new_attendees),
            "message": f"{attendee_email} has been added to '{event.get('summary')}'"
        }
    
    async def get_no_show_risks(
        self,
        days_ahead: int = 3,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Identify appointments that might be at risk of no-shows"""
        events_result = await self.get_upcoming_events(
            days_ahead=days_ahead,
            calendar_id=calendar_id
        )
        
        if "error" in events_result:
            return events_result
        
        events = events_result.get("events", [])
        
        at_risk = []
        for event in events:
            risk_factors = []
            risk_score = 0
            
            attendees = event.get("attendees", [])
            
            # Check for unconfirmed attendees
            unconfirmed = [a for a in attendees if a.get("response") == "needsAction"]
            if unconfirmed:
                risk_factors.append(f"{len(unconfirmed)} attendee(s) haven't responded")
                risk_score = risk_score + 30
            
            declined = [a for a in attendees if a.get("response") == "declined"]
            if declined:
                risk_factors.append(f"{len(declined)} attendee(s) declined")
                risk_score = risk_score + 50
            
            # No description might indicate hasty booking
            if not event.get("description"):
                risk_factors.append("No description provided")
                risk_score = risk_score + 10
            
            # No location for in-person meetings
            if not event.get("location") and not event.get("conference_data"):
                risk_factors.append("No location or video link")
                risk_score = risk_score + 20
            
            if risk_score > 20:
                at_risk.append({
                    "event": event,
                    "risk_score": min(risk_score, 100),
                    "risk_factors": risk_factors,
                    "recommendation": "Send reminder" if risk_score < 50 else "Consider rescheduling"
                })
        
        at_risk.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "at_risk_appointments": at_risk,
            "count": len(at_risk),
            "days_analyzed": days_ahead
        }
