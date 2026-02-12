from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.database import get_supabase


class GmailTools:
    """Tools for interacting with Gmail API"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._client_info = None
    
    async def _get_client(self) -> Dict[str, str]:
        """Get authenticated Gmail client info"""
        if not self._client_info:
            from app.api.integrations import get_gmail_client
            self._client_info = await get_gmail_client(self.user_id)
        return self._client_info
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Gmail API"""
        client_info = await self._get_client()
        base_url = "https://gmail.googleapis.com/gmail/v1"
        url = f"{base_url}/users/me/{endpoint}"
        
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
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code in (200, 204):
            if response.text:
                return response.json()
            return {"success": True}
        else:
            return {
                "error": f"Gmail API error: {response.status_code}",
                "details": response.text
            }
    
    def _decode_body(self, payload: Dict) -> str:
        """Decode email body from base64"""
        body = ""
        
        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        elif "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain" and part.get("body", {}).get("data"):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    break
                elif mime_type == "text/html" and part.get("body", {}).get("data") and not body:
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                elif "parts" in part:
                    # Handle nested multipart
                    body = self._decode_body(part)
                    if body:
                        break
        
        return body[:5000]  # Limit body length
    
    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header.get("name", "").lower() == name.lower():
                return header.get("value", "")
        return ""
    
    def _parse_email(self, message: Dict) -> Dict[str, Any]:
        """Parse Gmail message into structured format"""
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        
        return {
            "id": message.get("id"),
            "thread_id": message.get("threadId"),
            "snippet": message.get("snippet", ""),
            "subject": self._get_header(headers, "Subject"),
            "from": self._get_header(headers, "From"),
            "to": self._get_header(headers, "To"),
            "cc": self._get_header(headers, "Cc"),
            "date": self._get_header(headers, "Date"),
            "labels": message.get("labelIds", []),
            "body": self._decode_body(payload),
            "is_unread": "UNREAD" in message.get("labelIds", []),
            "is_important": "IMPORTANT" in message.get("labelIds", []),
            "is_starred": "STARRED" in message.get("labelIds", [])
        }
    
    async def get_emails(
        self,
        query: Optional[str] = None,
        label: Optional[str] = None,
        max_results: int = 20,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """Fetch emails from inbox with optional filtering"""
        q_parts = []
        
        if query:
            q_parts.append(query)
        if label:
            q_parts.append(f"label:{label}")
        if unread_only:
            q_parts.append("is:unread")
        
        params = {
            "maxResults": min(max_results, 50),
            "q": " ".join(q_parts) if q_parts else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        result = await self._make_request("GET", "messages", params=params)
        
        if "error" in result:
            return result
        
        messages = result.get("messages", [])
        emails = []
        
        for msg in messages[:max_results]:
            full_msg = await self._make_request("GET", f"messages/{msg['id']}")
            if "error" not in full_msg:
                emails.append(self._parse_email(full_msg))
        
        return {
            "emails": emails,
            "count": len(emails),
            "has_more": len(messages) > max_results
        }
    
    async def get_email_by_id(self, email_id: str) -> Dict[str, Any]:
        """Get a specific email by ID"""
        result = await self._make_request("GET", f"messages/{email_id}")
        
        if "error" in result:
            return result
        
        return {"email": self._parse_email(result)}
    
    async def triage_inbox(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze and categorize recent emails for triage"""
        cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)
        query = f"after:{cutoff.strftime('%Y/%m/%d')}"
        
        result = await self.get_emails(query=query, max_results=50)
        
        if "error" in result:
            return result
        
        emails = result.get("emails", [])
        
        # Categorize emails
        urgent = []
        needs_response = []
        informational = []
        low_priority = []
        
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency", "deadline"]
        response_keywords = ["please respond", "your thoughts", "let me know", "can you", "would you", "?"]
        low_priority_keywords = ["unsubscribe", "newsletter", "promotion", "marketing", "no-reply"]
        
        for email in emails:
            subject_lower = email["subject"].lower()
            snippet_lower = email["snippet"].lower()
            from_lower = email["from"].lower()
            combined = f"{subject_lower} {snippet_lower}"
            
            if any(kw in combined for kw in urgent_keywords) or email["is_important"]:
                urgent.append(email)
            elif any(kw in from_lower for kw in low_priority_keywords):
                low_priority.append(email)
            elif any(kw in combined for kw in response_keywords):
                needs_response.append(email)
            else:
                informational.append(email)
        
        return {
            "summary": {
                "total_emails": len(emails),
                "urgent": len(urgent),
                "needs_response": len(needs_response),
                "informational": len(informational),
                "low_priority": len(low_priority),
                "time_window_hours": time_window_hours
            },
            "urgent": urgent[:10],
            "needs_response": needs_response[:10],
            "informational": informational[:10],
            "low_priority": low_priority[:10],
            "triaged_at": datetime.utcnow().isoformat()
        }
    
    async def draft_response(
        self,
        email_id: str,
        response_body: str,
        include_original: bool = True
    ) -> Dict[str, Any]:
        """Create a draft reply to an email"""
        original = await self.get_email_by_id(email_id)
        
        if "error" in original:
            return original
        
        email = original["email"]
        
        # Build reply subject
        subject = email["subject"]
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"
        
        # Build reply body
        body = response_body
        if include_original:
            body += f"\n\n---\nOn {email['date']}, {email['from']} wrote:\n\n{email['snippet']}..."
        
        # Create MIME message
        message = MIMEText(body)
        message["To"] = email["from"]
        message["Subject"] = subject
        message["In-Reply-To"] = email_id
        message["References"] = email_id
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        draft_data = {
            "message": {
                "raw": raw,
                "threadId": email["thread_id"]
            }
        }
        
        result = await self._make_request("POST", "drafts", data=draft_data)
        
        if "error" in result:
            return result
        
        # Store draft reference
        supabase = get_supabase()
        supabase.table("email_drafts").insert({
            "user_id": self.user_id,
            "draft_id": result.get("id"),
            "original_email_id": email_id,
            "subject": subject,
            "to": email["from"],
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "draft_id": result.get("id"),
            "thread_id": email["thread_id"],
            "to": email["from"],
            "subject": subject,
            "status": "draft_created",
            "message": "Draft created successfully. Review and send when ready."
        }
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        reply_to_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an email (or send a draft)"""
        message = MIMEMultipart()
        message["To"] = to
        message["Subject"] = subject
        if cc:
            message["Cc"] = cc
        
        message.attach(MIMEText(body, "plain"))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        send_data = {"raw": raw}
        if reply_to_id:
            original = await self.get_email_by_id(reply_to_id)
            if "error" not in original:
                send_data["threadId"] = original["email"]["thread_id"]
        
        result = await self._make_request("POST", "messages/send", data=send_data)
        
        if "error" in result:
            return result
        
        return {
            "message_id": result.get("id"),
            "thread_id": result.get("threadId"),
            "to": to,
            "subject": subject,
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def schedule_followup(
        self,
        email_id: str,
        followup_date: str,
        followup_note: str
    ) -> Dict[str, Any]:
        """Schedule a follow-up reminder for an email"""
        email_result = await self.get_email_by_id(email_id)
        
        if "error" in email_result:
            return email_result
        
        email = email_result["email"]
        
        supabase = get_supabase()
        followup = supabase.table("email_followups").insert({
            "user_id": self.user_id,
            "email_id": email_id,
            "thread_id": email["thread_id"],
            "subject": email["subject"],
            "from_address": email["from"],
            "followup_date": followup_date,
            "followup_note": followup_note,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "followup_id": followup.data[0]["id"] if followup.data else None,
            "email_id": email_id,
            "subject": email["subject"],
            "followup_date": followup_date,
            "followup_note": followup_note,
            "status": "scheduled",
            "message": f"Follow-up scheduled for {followup_date}"
        }
    
    async def extract_action_items(
        self,
        email_id: str
    ) -> Dict[str, Any]:
        """Extract action items from an email"""
        email_result = await self.get_email_by_id(email_id)
        
        if "error" in email_result:
            return email_result
        
        email = email_result["email"]
        
        # This returns the email content for Claude to analyze
        # The actual extraction happens in the agent's reasoning
        return {
            "email_id": email_id,
            "subject": email["subject"],
            "from": email["from"],
            "date": email["date"],
            "body": email["body"],
            "snippet": email["snippet"],
            "message": "Email content retrieved. Analyze for action items."
        }
    
    async def apply_label(
        self,
        email_id: str,
        label_name: str
    ) -> Dict[str, Any]:
        """Apply a label to an email"""
        # First get or create the label
        labels_result = await self._make_request("GET", "labels")
        
        if "error" in labels_result:
            return labels_result
        
        label_id = None
        for label in labels_result.get("labels", []):
            if label["name"].lower() == label_name.lower():
                label_id = label["id"]
                break
        
        # Create label if it doesn't exist
        if not label_id:
            create_result = await self._make_request(
                "POST",
                "labels",
                data={"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
            )
            if "error" in create_result:
                return create_result
            label_id = create_result.get("id")
        
        # Apply label to email
        result = await self._make_request(
            "POST",
            f"messages/{email_id}/modify",
            data={"addLabelIds": [label_id]}
        )
        
        if "error" in result:
            return result
        
        return {
            "email_id": email_id,
            "label": label_name,
            "label_id": label_id,
            "status": "label_applied"
        }
    
    async def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """Mark an email as read"""
        result = await self._make_request(
            "POST",
            f"messages/{email_id}/modify",
            data={"removeLabelIds": ["UNREAD"]}
        )
        
        if "error" in result:
            return result
        
        return {"email_id": email_id, "status": "marked_read"}
    
    async def archive_email(self, email_id: str) -> Dict[str, Any]:
        """Archive an email (remove from inbox)"""
        result = await self._make_request(
            "POST",
            f"messages/{email_id}/modify",
            data={"removeLabelIds": ["INBOX"]}
        )
        
        if "error" in result:
            return result
        
        return {"email_id": email_id, "status": "archived"}
    
    async def get_followups_due(self) -> Dict[str, Any]:
        """Get follow-ups that are due"""
        supabase = get_supabase()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        result = supabase.table("email_followups") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("status", "scheduled") \
            .lte("followup_date", today) \
            .execute()
        
        return {
            "followups": result.data or [],
            "count": len(result.data or []),
            "as_of": today
        }
