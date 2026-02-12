from enum import Enum
from typing import Dict, Any


class AgentType(str, Enum):
    # Original 6 agents
    BOOKKEEPER = "bookkeeper"
    INBOX_COMMANDER = "inbox_commander"
    HIRE_WELL = "hire_well"
    CUSTOMER_CARE = "customer_care"
    SOCIAL_PILOT = "social_pilot"
    APPOINTMENT = "appointment"
    # New 6 agents
    COMPLIANCE_GUARD = "compliance_guard"
    VENDOR_NEGOTIATOR = "vendor_negotiator"
    PROPOSAL_PRO = "proposal_pro"
    INVENTORY_IQ = "inventory_iq"
    REPUTATION_SHIELD = "reputation_shield"
    CASHFLOW_COMMANDER = "cashflow_commander"


AGENT_REGISTRY: Dict[AgentType, Dict[str, Any]] = {
    # ============================================================
    # ORIGINAL 6 AGENTS
    # ============================================================
    
    AgentType.BOOKKEEPER: {
        "name": "BookkeeperAI",
        "description": "Automates bookkeeping tasks including transaction categorization, account reconciliation, anomaly detection, and financial reporting.",
        "price_monthly": 319,
        "category": "Finance",
        "features": [
            "Automatic transaction categorization",
            "Bank account reconciliation",
            "Expense anomaly detection",
            "Monthly financial reports",
            "Tax-ready categorization",
            "Multi-currency support"
        ],
        "integrations": ["QuickBooks", "Xero", "Plaid"],
        "required_integrations": ["quickbooks"],
        "status": "available",
        "tasks": [
            "categorize_transactions",
            "reconcile_accounts",
            "generate_report",
            "detect_anomalies",
            "prepare_tax_summary"
        ]
    },
    
    AgentType.INBOX_COMMANDER: {
        "name": "InboxCommanderAI",
        "description": "Manages your email inbox by triaging messages, drafting responses, scheduling follow-ups, and extracting action items.",
        "price_monthly": 239,
        "category": "Productivity",
        "features": [
            "Smart email triage and prioritization",
            "AI-drafted responses",
            "Automatic follow-up scheduling",
            "Action item extraction",
            "Meeting request handling",
            "Unsubscribe management"
        ],
        "integrations": ["Gmail", "Outlook", "Google Calendar"],
        "required_integrations": ["gmail"],
        "status": "available",
        "tasks": [
            "triage_inbox",
            "draft_response",
            "schedule_followup",
            "extract_action_items"
        ]
    },
    
    AgentType.HIRE_WELL: {
        "name": "HireWellAI",
        "description": "Streamlines hiring by screening resumes, scheduling interviews, sending status updates, and managing candidate communications.",
        "price_monthly": 479,
        "category": "Human Resources",
        "features": [
            "Resume screening and ranking",
            "Automated interview scheduling",
            "Candidate status updates",
            "Reference check coordination",
            "Job posting optimization",
            "Candidate pipeline tracking"
        ],
        "integrations": ["Gmail", "Google Calendar", "LinkedIn"],
        "required_integrations": ["gmail", "google_calendar"],
        "status": "available",
        "tasks": [
            "screen_resumes",
            "schedule_interview",
            "send_status_update",
            "coordinate_reference_check"
        ]
    },
    
    AgentType.CUSTOMER_CARE: {
        "name": "CustomerCareAI",
        "description": "Handles customer support by answering FAQs, resolving common issues, escalating complex cases, and tracking satisfaction.",
        "price_monthly": 399,
        "category": "Support",
        "features": [
            "24/7 automated support",
            "FAQ and knowledge base responses",
            "Smart escalation routing",
            "Satisfaction tracking",
            "Multi-channel support",
            "Response templates"
        ],
        "integrations": ["Zendesk", "Freshdesk", "Intercom", "Gmail"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "answer_ticket",
            "escalate_ticket",
            "generate_response",
            "track_satisfaction"
        ]
    },
    
    AgentType.SOCIAL_PILOT: {
        "name": "SocialPilotAI",
        "description": "Manages social media by creating posts, scheduling content, responding to comments, and reporting on engagement.",
        "price_monthly": 209,
        "category": "Marketing",
        "features": [
            "AI content generation",
            "Multi-platform scheduling",
            "Comment response drafting",
            "Engagement analytics",
            "Hashtag optimization",
            "Best time to post suggestions"
        ],
        "integrations": ["Meta", "Instagram", "LinkedIn", "Twitter"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "create_post",
            "schedule_content",
            "respond_to_comment",
            "generate_report"
        ]
    },
    
    AgentType.APPOINTMENT: {
        "name": "AppointmentAI",
        "description": "Handles scheduling by booking appointments, sending reminders, managing rescheduling, and reducing no-shows.",
        "price_monthly": 159,
        "category": "Productivity",
        "features": [
            "Natural language booking",
            "Automatic reminders",
            "Rescheduling management",
            "No-show reduction",
            "Calendar optimization",
            "Buffer time management"
        ],
        "integrations": ["Google Calendar", "Calendly", "Acuity"],
        "required_integrations": ["google_calendar"],
        "status": "available",
        "tasks": [
            "book_appointment",
            "send_reminder",
            "handle_reschedule",
            "optimize_schedule"
        ]
    },
    
    # ============================================================
    # NEW 6 AGENTS
    # ============================================================
    
    AgentType.COMPLIANCE_GUARD: {
        "name": "ComplianceGuardAI",
        "description": "Monitors regulations, tracks compliance deadlines, audits processes, and ensures your business stays compliant with all requirements.",
        "price_monthly": 559,
        "category": "Legal & Compliance",
        "features": [
            "Regulatory change monitoring",
            "Deadline tracking and alerts",
            "Compliance gap auditing",
            "Policy document generation",
            "Audit-ready reporting",
            "Industry-specific compliance"
        ],
        "integrations": ["Google Workspace", "DocuSign", "Gusto"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "monitor_regulations",
            "track_deadlines",
            "audit_compliance",
            "generate_policy",
            "prepare_audit_report"
        ]
    },
    
    AgentType.VENDOR_NEGOTIATOR: {
        "name": "VendorNegotiatorAI",
        "description": "Analyzes vendor contracts, benchmarks pricing, identifies savings opportunities, and automates renewal negotiations.",
        "price_monthly": 319,
        "category": "Procurement",
        "features": [
            "Contract inventory management",
            "Market rate benchmarking",
            "Savings opportunity identification",
            "Negotiation script generation",
            "Renewal automation",
            "Spend analytics"
        ],
        "integrations": ["QuickBooks", "Gmail", "Bank Feeds"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "analyze_contracts",
            "benchmark_pricing",
            "identify_savings",
            "draft_negotiation",
            "track_renewals"
        ]
    },
    
    AgentType.PROPOSAL_PRO: {
        "name": "ProposalProAI",
        "description": "Generates customized proposals, responds to RFPs, prices projects intelligently, and tracks deal progress to close.",
        "price_monthly": 399,
        "category": "Sales",
        "features": [
            "Custom proposal generation",
            "RFP response automation",
            "Intelligent project pricing",
            "Case study integration",
            "Follow-up automation",
            "Win/loss analysis"
        ],
        "integrations": ["HubSpot", "Salesforce", "Google Docs", "DocuSign"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "generate_proposal",
            "respond_to_rfp",
            "price_project",
            "track_proposal",
            "analyze_win_rate"
        ]
    },
    
    AgentType.INVENTORY_IQ: {
        "name": "InventoryIQAI",
        "description": "Forecasts demand, automates reordering, optimizes stock levels, and manages multi-location inventory intelligently.",
        "price_monthly": 369,
        "category": "Operations",
        "features": [
            "Demand forecasting",
            "Automated purchase orders",
            "Stock level optimization",
            "Supplier performance tracking",
            "Slow-mover identification",
            "Multi-location management"
        ],
        "integrations": ["Shopify", "Square", "QuickBooks", "ShipStation"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "forecast_demand",
            "generate_purchase_order",
            "optimize_inventory",
            "track_supplier",
            "identify_slow_movers"
        ]
    },
    
    AgentType.REPUTATION_SHIELD: {
        "name": "ReputationShieldAI",
        "description": "Monitors online reviews, drafts responses, requests reviews from happy customers, and tracks brand sentiment.",
        "price_monthly": 259,
        "category": "Marketing",
        "features": [
            "Multi-platform review monitoring",
            "AI response generation",
            "Review request campaigns",
            "Sentiment analysis",
            "Competitor tracking",
            "Crisis alert system"
        ],
        "integrations": ["Google Business", "Yelp", "Facebook", "Email"],
        "required_integrations": [],
        "status": "available",
        "tasks": [
            "monitor_reviews",
            "draft_response",
            "request_reviews",
            "analyze_sentiment",
            "track_competitors"
        ]
    },
    
    AgentType.CASHFLOW_COMMANDER: {
        "name": "CashFlowCommanderAI",
        "description": "Projects cash flow, prioritizes collections, optimizes payment timing, and alerts you to potential cash crunches.",
        "price_monthly": 479,
        "category": "Finance",
        "features": [
            "30/60/90 day cash projections",
            "Collection prioritization",
            "Payment timing optimization",
            "Cash crunch alerts",
            "Invoice reminder automation",
            "Customer payment scoring"
        ],
        "integrations": ["QuickBooks", "Xero", "Bank Accounts", "Stripe"],
        "required_integrations": ["quickbooks"],
        "status": "available",
        "tasks": [
            "project_cashflow",
            "prioritize_collections",
            "optimize_payments",
            "send_invoice_reminder",
            "score_customer_risk"
        ]
    }
}


def get_agent_info(agent_type: AgentType) -> Dict[str, Any]:
    """Get information about a specific agent"""
    return AGENT_REGISTRY.get(agent_type, {})


def get_available_agents() -> list:
    """Get all available agents"""
    return [
        {"type": agent_type.value, **info}
        for agent_type, info in AGENT_REGISTRY.items()
        if info.get("status") == "available"
    ]


def get_agent_by_category(category: str) -> list:
    """Get agents by category"""
    return [
        {"type": agent_type.value, **info}
        for agent_type, info in AGENT_REGISTRY.items()
        if info.get("category") == category
    ]
