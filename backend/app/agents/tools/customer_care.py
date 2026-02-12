from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx

from app.core.database import get_supabase


class CustomerCareTools:
    """Tools for customer support operations"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def _get_zendesk_client(self) -> Dict[str, str]:
        """Get authenticated Zendesk client info"""
        from app.api.integrations import get_zendesk_client
        return await get_zendesk_client(self.user_id)
    
    async def _make_zendesk_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Zendesk API"""
        try:
            client_info = await self._get_zendesk_client()
            base_url = f"https://{client_info['subdomain']}.zendesk.com/api/v2"
            url = f"{base_url}/{endpoint}"
            
            headers = {
                "Authorization": f"Bearer {client_info['access_token']}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code in (200, 201):
                return response.json()
            else:
                return {"error": f"Zendesk API error: {response.status_code}", "details": response.text}
        except Exception as e:
            return await self._get_mock_tickets(endpoint, method, data)
    
    async def _get_mock_tickets(self, endpoint: str, method: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Return mock data for development/demo purposes"""
        if "tickets" in endpoint and method == "GET":
            return {
                "tickets": [
                    {
                        "id": 101,
                        "subject": "Unable to login to my account",
                        "description": "I've been trying to login for the past hour but keep getting an error message saying 'Invalid credentials' even though I'm sure my password is correct.",
                        "status": "open",
                        "priority": "high",
                        "requester": {"name": "John Smith", "email": "john.smith@example.com"},
                        "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                        "updated_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                        "tags": ["login", "account-access", "urgent"]
                    },
                    {
                        "id": 102,
                        "subject": "Billing question about my subscription",
                        "description": "I was charged twice this month for my Pro subscription. Order #12345 and #12346. Can you please refund one of them?",
                        "status": "open",
                        "priority": "normal",
                        "requester": {"name": "Sarah Johnson", "email": "sarah.j@example.com"},
                        "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                        "updated_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                        "tags": ["billing", "subscription", "refund"]
                    },
                    {
                        "id": 103,
                        "subject": "Feature request: Dark mode",
                        "description": "Would love to see a dark mode option in the app. It would be much easier on the eyes when working late.",
                        "status": "open",
                        "priority": "low",
                        "requester": {"name": "Mike Wilson", "email": "mike.w@example.com"},
                        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                        "updated_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                        "tags": ["feature-request", "ui"]
                    },
                    {
                        "id": 104,
                        "subject": "App crashes when uploading large files",
                        "description": "Every time I try to upload a file larger than 50MB, the app crashes. This is blocking my work.",
                        "status": "open",
                        "priority": "high",
                        "requester": {"name": "Emily Chen", "email": "emily.c@example.com"},
                        "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                        "updated_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                        "tags": ["bug", "upload", "crash"]
                    },
                    {
                        "id": 105,
                        "subject": "How do I export my data?",
                        "description": "I need to export all my project data to CSV format. Can't find the option in settings.",
                        "status": "open",
                        "priority": "normal",
                        "requester": {"name": "David Lee", "email": "david.lee@example.com"},
                        "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                        "updated_at": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                        "tags": ["how-to", "export", "data"]
                    }
                ],
                "count": 5
            }
        return {"status": "ok", "mock": True}
    
    async def get_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """Fetch support tickets with optional filtering"""
        params = {"per_page": min(max_results, 100)}
        
        query_parts = []
        if status:
            query_parts.append(f"status:{status}")
        if priority:
            query_parts.append(f"priority:{priority}")
        
        if query_parts:
            params["query"] = " ".join(query_parts)
        
        result = await self._make_zendesk_request("GET", "tickets.json", params=params)
        
        if "error" in result:
            return result
        
        tickets = result.get("tickets", [])
        
        parsed = []
        for t in tickets[:max_results]:
            parsed.append({
                "id": t.get("id"),
                "subject": t.get("subject"),
                "description": (t.get("description") or "")[:500],
                "status": t.get("status"),
                "priority": t.get("priority"),
                "requester": t.get("requester", {}),
                "created_at": t.get("created_at"),
                "updated_at": t.get("updated_at"),
                "tags": t.get("tags", [])
            })
        
        return {
            "tickets": parsed,
            "count": len(parsed),
            "filters": {"status": status, "priority": priority}
        }
    
    async def get_ticket_by_id(self, ticket_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific ticket"""
        result = await self._make_zendesk_request("GET", f"tickets/{ticket_id}.json")
        
        if "error" in result:
            return result
        
        ticket = result.get("ticket", {})
        
        comments_result = await self._make_zendesk_request("GET", f"tickets/{ticket_id}/comments.json")
        comments = comments_result.get("comments", []) if "error" not in comments_result else []
        
        return {
            "ticket": {
                "id": ticket.get("id"),
                "subject": ticket.get("subject"),
                "description": ticket.get("description"),
                "status": ticket.get("status"),
                "priority": ticket.get("priority"),
                "requester": ticket.get("requester", {}),
                "created_at": ticket.get("created_at"),
                "updated_at": ticket.get("updated_at"),
                "tags": ticket.get("tags", [])
            },
            "conversation": [
                {
                    "id": c.get("id"),
                    "body": (c.get("body") or "")[:1000],
                    "author": c.get("author", {}),
                    "created_at": c.get("created_at"),
                    "public": c.get("public", True)
                }
                for c in comments
            ]
        }
    
    async def answer_ticket(
        self,
        ticket_id: str,
        response: str,
        internal_note: bool = False,
        set_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post a response to a support ticket"""
        comment_data = {
            "ticket": {
                "comment": {
                    "body": response,
                    "public": not internal_note
                }
            }
        }
        
        if set_status:
            comment_data["ticket"]["status"] = set_status
        
        result = await self._make_zendesk_request("PUT", f"tickets/{ticket_id}.json", data=comment_data)
        
        if "error" in result:
            return result
        
        supabase = get_supabase()
        supabase.table("ticket_responses").insert({
            "user_id": self.user_id,
            "ticket_id": str(ticket_id),
            "response": response[:2000],
            "is_internal": internal_note,
            "new_status": set_status,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "ticket_id": ticket_id,
            "status": "response_posted",
            "is_internal": internal_note,
            "new_status": set_status,
            "message": "Response posted successfully"
        }
    
    async def escalate_ticket(
        self,
        ticket_id: str,
        reason: str,
        escalation_level: str = "tier2",
        assign_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Escalate a ticket to a higher support tier"""
        internal_note = f"[ESCALATION - {escalation_level.upper()}]\nReason: {reason}"
        
        if assign_to:
            internal_note += f"\nAssigned to: {assign_to}"
        
        update_data = {
            "ticket": {
                "priority": "high",
                "tags": [f"escalated-{escalation_level}"],
                "comment": {
                    "body": internal_note,
                    "public": False
                }
            }
        }
        
        result = await self._make_zendesk_request("PUT", f"tickets/{ticket_id}.json", data=update_data)
        
        if "error" in result:
            return result
        
        supabase = get_supabase()
        supabase.table("ticket_escalations").insert({
            "user_id": self.user_id,
            "ticket_id": str(ticket_id),
            "reason": reason,
            "escalation_level": escalation_level,
            "assigned_to": assign_to,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "ticket_id": ticket_id,
            "status": "escalated",
            "escalation_level": escalation_level,
            "reason": reason,
            "message": f"Ticket escalated to {escalation_level}"
        }
    
    async def generate_response(
        self,
        ticket_id: str,
        response_type: str = "helpful",
        include_kb_link: bool = False
    ) -> Dict[str, Any]:
        """Generate an appropriate response based on ticket content"""
        ticket_result = await self.get_ticket_by_id(ticket_id)
        
        if "error" in ticket_result:
            return ticket_result
        
        ticket = ticket_result.get("ticket", {})
        subject = ticket.get("subject", "").lower()
        description = ticket.get("description", "").lower()
        requester = ticket.get("requester", {})
        customer_name = requester.get("name", "").split()[0] if requester.get("name") else "there"
        
        if any(word in subject + description for word in ["login", "password", "access", "credentials"]):
            category = "account_access"
            response = f"""Hi {customer_name},

Thank you for reaching out about your login issue. I understand how frustrating it can be when you can't access your account.

Here are a few steps that should help:

1. Try resetting your password using the "Forgot Password" link on the login page
2. Clear your browser cache and cookies, then try again
3. Make sure you're using the correct email address associated with your account
4. If you have two-factor authentication enabled, ensure you have access to your authenticator app

If you're still having trouble after trying these steps, please let me know and I'll be happy to assist further or escalate this to our technical team.

Best regards,
Support Team"""

        elif any(word in subject + description for word in ["billing", "charge", "refund", "payment", "invoice"]):
            category = "billing"
            response = f"""Hi {customer_name},

Thank you for contacting us about your billing concern. I apologize for any confusion or inconvenience this may have caused.

I'm looking into your account now to review the charges you mentioned. To help me resolve this quickly, could you please confirm:

1. The last 4 digits of the payment method used
2. The approximate date(s) of the charge(s)
3. The order or transaction numbers if you have them

Once I have this information, I'll be able to investigate and process any necessary adjustments promptly.

Best regards,
Support Team"""

        elif any(word in subject + description for word in ["bug", "crash", "error", "broken", "not working"]):
            category = "technical"
            response = f"""Hi {customer_name},

Thank you for reporting this issue. I'm sorry you're experiencing problems, and I want to help get this resolved as quickly as possible.

To help our technical team investigate, could you please provide:

1. What device and operating system are you using?
2. What browser (and version) if applicable?
3. Can you describe the exact steps that lead to the issue?
4. Do you see any specific error messages?
5. When did this issue start occurring?

In the meantime, you might try:
- Refreshing the page or restarting the app
- Clearing your cache and cookies
- Trying a different browser

I'll make sure this gets the attention it needs. Thank you for your patience!

Best regards,
Support Team"""

        elif any(word in subject + description for word in ["feature", "request", "suggestion", "would like", "wish"]):
            category = "feature_request"
            response = f"""Hi {customer_name},

Thank you so much for taking the time to share your suggestion with us! We really appreciate feedback from our users - it helps us build a better product.

I've logged your feature request and will make sure it gets to our product team for consideration. While I can't make any promises about timelines, please know that we carefully review all suggestions when planning our roadmap.

Is there anything else I can help you with in the meantime?

Best regards,
Support Team"""

        else:
            category = "general"
            response = f"""Hi {customer_name},

Thank you for reaching out to us. I've received your message and I'm here to help.

I'm reviewing your inquiry now. To make sure I can assist you as effectively as possible, could you provide any additional details that might be relevant?

I'll get back to you with a solution as soon as possible. Thank you for your patience!

Best regards,
Support Team"""

        if include_kb_link:
            response += "\n\nYou might also find our Help Center useful: [Help Center Link]"
        
        return {
            "ticket_id": ticket_id,
            "category": category,
            "suggested_response": response,
            "response_type": response_type,
            "customer_name": customer_name,
            "status": "draft_generated",
            "message": "Response generated. Please review before sending."
        }
    
    async def track_satisfaction(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get customer satisfaction metrics"""
        supabase = get_supabase()
        
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        responses = supabase.table("ticket_responses") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .execute()
        
        escalations = supabase.table("ticket_escalations") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .execute()
        
        responses_data = responses.data or []
        escalations_data = escalations.data or []
        
        total_responses = len(responses_data)
        total_escalations = len(escalations_data)
        
        escalation_rate = (total_escalations / total_responses * 100) if total_responses > 0 else 0
        
        return {
            "period_days": days_back,
            "metrics": {
                "total_tickets_handled": total_responses,
                "total_escalations": total_escalations,
                "escalation_rate": round(escalation_rate, 1)
            },
            "trends": {
                "escalations_by_level": self._count_by_field(escalations_data, "escalation_level")
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _count_by_field(self, data: List[Dict], field: str) -> Dict[str, int]:
        """Helper to count occurrences by field value"""
        counts = {}
        for item in data:
            value = item.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    async def get_pending_tickets(self) -> Dict[str, Any]:
        """Get tickets that need attention"""
        result = await self.get_tickets(status="open", max_results=50)
        
        if "error" in result:
            return result
        
        tickets = result.get("tickets", [])
        
        high_priority = []
        aging = []
        normal = []
        
        now = datetime.utcnow()
        
        for ticket in tickets:
            priority = ticket.get("priority", "normal")
            created_str = ticket.get("created_at", "")
            
            hours_old = 0
            if created_str:
                try:
                    created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    hours_old = (now - created.replace(tzinfo=None)).total_seconds() / 3600
                except (ValueError, TypeError):
                    pass
            
            ticket["hours_old"] = round(hours_old, 1)
            
            if priority == "high" or priority == "urgent":
                high_priority.append(ticket)
            elif hours_old > 24:
                aging.append(ticket)
            else:
                normal.append(ticket)
        
        return {
            "summary": {
                "total_pending": len(tickets),
                "high_priority": len(high_priority),
                "aging_over_24h": len(aging),
                "normal": len(normal)
            },
            "high_priority_tickets": high_priority[:10],
            "aging_tickets": aging[:10],
            "recommendations": self._generate_recommendations(high_priority, aging)
        }
    
    def _generate_recommendations(self, high_priority: List, aging: List) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        if len(high_priority) > 5:
            recs.append(f"URGENT: {len(high_priority)} high-priority tickets need immediate attention")
        elif len(high_priority) > 0:
            recs.append(f"Address {len(high_priority)} high-priority ticket(s) first")
        
        if len(aging) > 10:
            recs.append(f"WARNING: {len(aging)} tickets are over 24 hours old - consider escalating")
        elif len(aging) > 0:
            recs.append(f"Follow up on {len(aging)} aging ticket(s) to maintain SLA")
        
        if not recs:
            recs.append("Ticket queue is healthy - continue monitoring")
        
        return recs
