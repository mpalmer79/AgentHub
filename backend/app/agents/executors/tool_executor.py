from typing import Dict, Any
from app.agents.registry import AgentType


class ToolExecutor:
    """Handles tool execution routing for all agents"""
    
    def __init__(self, agent_type: AgentType, tools: Dict[str, Any]):
        self.agent_type = agent_type
        self.tools = tools
    
    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Route and execute a tool call"""
        executor_map = {
            AgentType.BOOKKEEPER: self._execute_bookkeeper,
            AgentType.INBOX_COMMANDER: self._execute_inbox,
            AgentType.APPOINTMENT: self._execute_appointment,
            AgentType.HIRE_WELL: self._execute_hiring,
            AgentType.CASHFLOW_COMMANDER: self._execute_cashflow,
            AgentType.REPUTATION_SHIELD: self._execute_reputation,
            AgentType.CUSTOMER_CARE: self._execute_customer_care,
            AgentType.SOCIAL_PILOT: self._execute_social_pilot,
            AgentType.COMPLIANCE_GUARD: self._execute_compliance,
            AgentType.VENDOR_NEGOTIATOR: self._execute_vendor,
            AgentType.PROPOSAL_PRO: self._execute_proposal,
            AgentType.INVENTORY_IQ: self._execute_inventory,
        }
        
        executor = executor_map.get(self.agent_type)
        if executor:
            return await executor(tool_name, tool_input)
        
        return {"error": f"Unknown agent type: {self.agent_type}"}
    
    async def _execute_bookkeeper(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        qb_tools = self.tools.get("quickbooks")
        if not qb_tools:
            return {"error": "QuickBooks tools not initialized"}
        
        tool_map = {
            "get_transactions": qb_tools.get_transactions,
            "categorize_transaction": qb_tools.categorize_transaction,
            "get_accounts": qb_tools.get_accounts,
            "get_account_balance": qb_tools.get_account_balance,
            "create_expense_report": qb_tools.create_expense_report,
            "flag_for_review": qb_tools.flag_for_review,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_inbox(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        gmail_tools = self.tools.get("gmail")
        if not gmail_tools:
            return {"error": "Gmail tools not initialized"}
        
        tool_map = {
            "get_emails": gmail_tools.get_emails,
            "get_email_by_id": gmail_tools.get_email_by_id,
            "triage_inbox": gmail_tools.triage_inbox,
            "draft_response": gmail_tools.draft_response,
            "send_email": gmail_tools.send_email,
            "schedule_followup": gmail_tools.schedule_followup,
            "extract_action_items": gmail_tools.extract_action_items,
            "apply_label": gmail_tools.apply_label,
            "mark_as_read": gmail_tools.mark_as_read,
            "archive_email": gmail_tools.archive_email,
            "get_followups_due": lambda: gmail_tools.get_followups_due(),
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            if tool_name == "get_followups_due":
                return await tool_fn()
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_appointment(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        cal_tools = self.tools.get("calendar")
        if not cal_tools:
            return {"error": "Calendar tools not initialized"}
        
        tool_map = {
            "get_upcoming_events": cal_tools.get_upcoming_events,
            "get_event_by_id": cal_tools.get_event_by_id,
            "find_available_slots": cal_tools.find_available_slots,
            "book_appointment": cal_tools.book_appointment,
            "reschedule_appointment": cal_tools.reschedule_appointment,
            "cancel_appointment": cal_tools.cancel_appointment,
            "send_reminder": cal_tools.send_reminder,
            "get_todays_schedule": cal_tools.get_todays_schedule,
            "check_conflicts": cal_tools.check_conflicts,
            "add_attendee": cal_tools.add_attendee,
            "get_no_show_risks": cal_tools.get_no_show_risks,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_hiring(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        hiring_tools = self.tools.get("hiring")
        if not hiring_tools:
            return {"error": "Hiring tools not initialized"}
        
        tool_map = {
            "get_candidate_emails": hiring_tools.get_candidate_emails,
            "screen_resume": hiring_tools.screen_resume,
            "schedule_interview": hiring_tools.schedule_interview,
            "send_status_update": hiring_tools.send_status_update,
            "get_pipeline_status": hiring_tools.get_pipeline_status,
            "coordinate_reference_check": hiring_tools.coordinate_reference_check,
            "get_candidates_needing_followup": hiring_tools.get_candidates_needing_followup,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_cashflow(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        cashflow_tools = self.tools.get("cashflow")
        if not cashflow_tools:
            return {"error": "CashFlow tools not initialized"}
        
        tool_map = {
            "project_cashflow": cashflow_tools.project_cashflow,
            "prioritize_collections": cashflow_tools.prioritize_collections,
            "optimize_payments": cashflow_tools.optimize_payments,
            "send_invoice_reminder": cashflow_tools.send_invoice_reminder,
            "score_customer_risk": cashflow_tools.score_customer_risk,
            "get_cash_alerts": lambda: cashflow_tools.get_cash_alerts(),
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            if tool_name == "get_cash_alerts":
                return await tool_fn()
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_reputation(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        reputation_tools = self.tools.get("reputation")
        if not reputation_tools:
            return {"error": "Reputation tools not initialized"}
        
        tool_map = {
            "monitor_reviews": reputation_tools.monitor_reviews,
            "draft_response": reputation_tools.draft_response,
            "request_reviews": reputation_tools.request_reviews,
            "analyze_sentiment": reputation_tools.analyze_sentiment,
            "track_competitors": reputation_tools.track_competitors,
            "get_crisis_alerts": lambda: reputation_tools.get_crisis_alerts(),
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            if tool_name == "get_crisis_alerts":
                return await tool_fn()
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_customer_care(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        care_tools = self.tools.get("customer_care")
        if not care_tools:
            return {"error": "CustomerCare tools not initialized"}
        
        tool_map = {
            "get_tickets": care_tools.get_tickets,
            "get_ticket_by_id": care_tools.get_ticket_by_id,
            "answer_ticket": care_tools.answer_ticket,
            "escalate_ticket": care_tools.escalate_ticket,
            "generate_response": care_tools.generate_response,
            "track_satisfaction": care_tools.track_satisfaction,
            "get_pending_tickets": lambda: care_tools.get_pending_tickets(),
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            if tool_name == "get_pending_tickets":
                return await tool_fn()
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_social_pilot(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        social_tools = self.tools.get("social_pilot")
        if not social_tools:
            return {"error": "SocialPilot tools not initialized"}
        
        tool_map = {
            "create_post": social_tools.create_post,
            "schedule_content": social_tools.schedule_content,
            "get_scheduled_posts": social_tools.get_scheduled_posts,
            "respond_to_comment": social_tools.respond_to_comment,
            "get_comments": social_tools.get_comments,
            "generate_content_ideas": social_tools.generate_content_ideas,
            "generate_report": social_tools.generate_report,
            "get_analytics": social_tools.get_analytics,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_compliance(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        compliance_tools = self.tools.get("compliance")
        if not compliance_tools:
            return {"error": "Compliance tools not initialized"}
        
        tool_map = {
            "monitor_regulations": compliance_tools.monitor_regulations,
            "track_deadlines": compliance_tools.track_deadlines,
            "audit_compliance": compliance_tools.audit_compliance,
            "generate_policy": compliance_tools.generate_policy,
            "prepare_audit_report": compliance_tools.prepare_audit_report,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_vendor(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        vendor_tools = self.tools.get("vendor")
        if not vendor_tools:
            return {"error": "Vendor tools not initialized"}
        
        tool_map = {
            "analyze_contracts": vendor_tools.analyze_contracts,
            "benchmark_pricing": vendor_tools.benchmark_pricing,
            "identify_savings": vendor_tools.identify_savings,
            "draft_negotiation": vendor_tools.draft_negotiation,
            "track_renewals": vendor_tools.track_renewals,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_proposal(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        proposal_tools = self.tools.get("proposal")
        if not proposal_tools:
            return {"error": "Proposal tools not initialized"}
        
        tool_map = {
            "generate_proposal": proposal_tools.generate_proposal,
            "respond_to_rfp": proposal_tools.respond_to_rfp,
            "price_project": proposal_tools.price_project,
            "track_proposal": proposal_tools.track_proposal,
            "analyze_win_rate": proposal_tools.analyze_win_rate,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _execute_inventory(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        inventory_tools = self.tools.get("inventory")
        if not inventory_tools:
            return {"error": "Inventory tools not initialized"}
        
        tool_map = {
            "forecast_demand": inventory_tools.forecast_demand,
            "generate_purchase_order": inventory_tools.generate_purchase_order,
            "optimize_inventory": inventory_tools.optimize_inventory,
            "track_supplier": inventory_tools.track_supplier,
            "identify_slow_movers": inventory_tools.identify_slow_movers,
        }
        
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return await tool_fn(**tool_input)
        return {"error": f"Unknown tool: {tool_name}"}
