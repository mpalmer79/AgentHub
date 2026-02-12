from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx

from app.core.database import get_supabase


class ProposalTools:
    """Tools for proposal generation and deal management"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def generate_proposal(
        self,
        client_name: str,
        project_title: str,
        project_description: str,
        services: List[str],
        estimated_value: Optional[float] = None,
        timeline_weeks: Optional[int] = None,
        template: str = "standard"
    ) -> Dict[str, Any]:
        """Generate a customized proposal for a client"""
        supabase = get_supabase()
        
        # Define proposal templates
        templates = {
            "standard": {
                "sections": ["executive_summary", "scope", "approach", "timeline", "pricing", "terms"],
                "tone": "professional"
            },
            "detailed": {
                "sections": ["executive_summary", "company_overview", "understanding", "scope", "methodology", "team", "timeline", "pricing", "case_studies", "terms"],
                "tone": "comprehensive"
            },
            "brief": {
                "sections": ["summary", "scope", "pricing", "next_steps"],
                "tone": "concise"
            }
        }
        
        selected_template = templates.get(template, templates["standard"])
        
        # Generate proposal content
        proposal_content = {
            "executive_summary": f"""We are pleased to submit this proposal for {project_title} for {client_name}. 

Based on our understanding of your requirements, we are confident in our ability to deliver a solution that meets your objectives and exceeds expectations.

{project_description}""",
            
            "company_overview": """With years of experience delivering successful projects, our team brings deep expertise and a proven track record of client satisfaction. We pride ourselves on transparent communication, on-time delivery, and measurable results.""",
            
            "understanding": f"""Based on our discussions, we understand that {client_name} is looking to:
- Address key business challenges through {project_title}
- Achieve measurable improvements in efficiency and outcomes
- Implement a solution that scales with future growth""",
            
            "scope": f"""The proposed scope of work includes:

{chr(10).join(f'• {service}' for service in services)}

Deliverables:
- Comprehensive project documentation
- Regular progress reports and updates
- Final delivery with quality assurance
- Post-project support period""",
            
            "methodology": """Our proven methodology ensures successful project delivery:

1. Discovery & Planning - Detailed requirements gathering and project planning
2. Design & Development - Iterative approach with regular client feedback
3. Testing & Quality Assurance - Comprehensive testing protocols
4. Deployment & Training - Smooth rollout with full team training
5. Support & Optimization - Ongoing support and continuous improvement""",
            
            "team": """Your project will be supported by our experienced team:
- Project Manager - Single point of contact for all communications
- Subject Matter Experts - Deep expertise in relevant domains
- Quality Assurance - Dedicated QA resources
- Support Team - Responsive post-delivery support""",
            
            "timeline": f"""Proposed Timeline: {timeline_weeks or 8} weeks

Phase 1: Discovery & Planning (Weeks 1-2)
Phase 2: Design & Development (Weeks 3-{(timeline_weeks or 8) - 2})
Phase 3: Testing & QA (Week {(timeline_weeks or 8) - 1})
Phase 4: Deployment & Training (Week {timeline_weeks or 8})

*Timeline subject to scope confirmation and resource availability""",
            
            "pricing": self._generate_pricing_section(services, estimated_value),
            
            "case_studies": """Recent Success Stories:

Client A - Similar project delivered on time and 15% under budget
Client B - Achieved 40% efficiency improvement within 6 months
Client C - Successful implementation with 98% user adoption rate""",
            
            "terms": """Standard Terms:
- Payment: 50% upon signing, 50% upon completion
- Validity: This proposal is valid for 30 days
- Changes: Scope changes subject to change order process
- Confidentiality: All project information treated as confidential

Next Steps:
1. Review and discuss any questions
2. Sign proposal to initiate project
3. Kick-off meeting within 5 business days of signing""",
            
            "summary": f"""Proposal for {project_title}

We propose to deliver the following for {client_name}:
{chr(10).join(f'• {service}' for service in services)}

Investment: ${estimated_value or 'TBD':,.2f}
Timeline: {timeline_weeks or 8} weeks""",
            
            "next_steps": """To proceed:
1. Reply to accept this proposal
2. We'll schedule a kick-off call
3. Project begins within one week of acceptance"""
        }
        
        # Build proposal based on template sections
        proposal_sections = []
        for section in selected_template["sections"]:
            if section in proposal_content:
                proposal_sections.append({
                    "section": section.replace("_", " ").title(),
                    "content": proposal_content[section]
                })
        
        # Save proposal to database
        proposal_id = f"prop_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        supabase.table("proposals").insert({
            "id": proposal_id,
            "user_id": self.user_id,
            "client_name": client_name,
            "project_title": project_title,
            "project_description": project_description,
            "services": services,
            "estimated_value": estimated_value,
            "timeline_weeks": timeline_weeks,
            "template": template,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "proposal_id": proposal_id,
            "client_name": client_name,
            "project_title": project_title,
            "template": template,
            "sections": proposal_sections,
            "estimated_value": estimated_value,
            "timeline_weeks": timeline_weeks or 8,
            "status": "draft",
            "valid_until": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _generate_pricing_section(self, services: List[str], estimated_value: Optional[float]) -> str:
        """Generate pricing section content"""
        if estimated_value:
            return f"""Investment Summary:

Total Project Investment: ${estimated_value:,.2f}

This investment includes:
{chr(10).join(f'• {service}' for service in services)}

Payment Schedule:
- 50% upon proposal acceptance: ${estimated_value * 0.5:,.2f}
- 50% upon project completion: ${estimated_value * 0.5:,.2f}

*Pricing valid for 30 days from proposal date"""
        else:
            return """Investment Summary:

Pricing will be confirmed following detailed scope review.

Factors affecting final pricing:
- Scope complexity and requirements
- Timeline and resource needs
- Additional services requested

We will provide a detailed quote within 48 hours of scope confirmation."""
    
    async def respond_to_rfp(
        self,
        rfp_title: str,
        client_name: str,
        requirements: List[str],
        deadline: str,
        budget_range: Optional[str] = None,
        evaluation_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a response to an RFP"""
        supabase = get_supabase()
        
        # Map requirements to response sections
        requirement_responses = []
        for i, req in enumerate(requirements, 1):
            requirement_responses.append({
                "requirement_number": i,
                "requirement": req,
                "response": f"We fully understand and can meet this requirement. Our approach includes dedicated resources and proven methodologies to deliver {req.lower()}.",
                "compliance": "full"
            })
        
        # Generate executive summary
        executive_summary = f"""Thank you for the opportunity to respond to the {rfp_title} RFP.

We have carefully reviewed your requirements and are confident in our ability to deliver a comprehensive solution for {client_name}. Our response demonstrates:

- Full compliance with all stated requirements
- Proven experience with similar projects
- Competitive pricing within your budget parameters
- Commitment to your timeline and success criteria

We look forward to discussing how we can partner with {client_name} to achieve your objectives."""
        
        # Generate technical approach
        technical_approach = f"""Our technical approach for {rfp_title} includes:

1. Requirements Analysis
   - Detailed review of all {len(requirements)} requirements
   - Gap analysis and solution mapping
   - Risk identification and mitigation planning

2. Solution Design
   - Architecture aligned with your specifications
   - Scalability and performance considerations
   - Security and compliance integration

3. Implementation Strategy
   - Phased delivery approach
   - Regular milestone reviews
   - Quality assurance at each phase

4. Knowledge Transfer
   - Comprehensive documentation
   - Training programs for your team
   - Ongoing support framework"""
        
        # Pricing approach
        pricing_approach = f"""Pricing Approach:

{'Budget Range Acknowledged: ' + budget_range if budget_range else 'We will provide detailed pricing based on final scope confirmation.'}

Our pricing model includes:
- Transparent cost breakdown by deliverable
- No hidden fees or surprise charges
- Flexible payment terms available
- Volume discounts for multi-year engagements

Detailed pricing will be provided in the Cost Proposal section."""
        
        # Generate compliance matrix
        compliance_matrix = []
        for i, req in enumerate(requirements, 1):
            compliance_matrix.append({
                "req_id": f"REQ-{i:03d}",
                "requirement_summary": req[:50] + "..." if len(req) > 50 else req,
                "compliance_status": "Compliant",
                "response_reference": f"Section 3.{i}"
            })
        
        # Save RFP response
        rfp_id = f"rfp_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        supabase.table("rfp_responses").insert({
            "id": rfp_id,
            "user_id": self.user_id,
            "rfp_title": rfp_title,
            "client_name": client_name,
            "requirements_count": len(requirements),
            "deadline": deadline,
            "budget_range": budget_range,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "rfp_response_id": rfp_id,
            "rfp_title": rfp_title,
            "client_name": client_name,
            "deadline": deadline,
            "response_sections": {
                "executive_summary": executive_summary,
                "technical_approach": technical_approach,
                "requirement_responses": requirement_responses,
                "pricing_approach": pricing_approach,
                "compliance_matrix": compliance_matrix
            },
            "compliance_summary": {
                "total_requirements": len(requirements),
                "fully_compliant": len(requirements),
                "partially_compliant": 0,
                "non_compliant": 0
            },
            "evaluation_criteria_addressed": evaluation_criteria or [],
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def price_project(
        self,
        project_type: str,
        scope_items: List[str],
        complexity: str = "medium",
        timeline_preference: str = "standard",
        include_options: bool = True
    ) -> Dict[str, Any]:
        """Intelligently price a project based on scope and complexity"""
        
        # Base pricing by project type (hourly rates and typical hours)
        project_pricing = {
            "consulting": {"base_rate": 150, "typical_hours": 40},
            "development": {"base_rate": 125, "typical_hours": 160},
            "design": {"base_rate": 100, "typical_hours": 80},
            "marketing": {"base_rate": 125, "typical_hours": 60},
            "implementation": {"base_rate": 135, "typical_hours": 120},
            "training": {"base_rate": 175, "typical_hours": 24},
            "support": {"base_rate": 100, "typical_hours": 40},
            "strategy": {"base_rate": 200, "typical_hours": 32}
        }
        
        # Complexity multipliers
        complexity_multipliers = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3,
            "very_high": 1.6
        }
        
        # Timeline multipliers
        timeline_multipliers = {
            "rushed": 1.25,
            "accelerated": 1.15,
            "standard": 1.0,
            "flexible": 0.95
        }
        
        # Get base pricing
        base = project_pricing.get(project_type.lower(), {"base_rate": 125, "typical_hours": 80})
        complexity_mult = complexity_multipliers.get(complexity.lower(), 1.0)
        timeline_mult = timeline_multipliers.get(timeline_preference.lower(), 1.0)
        
        # Calculate line items
        line_items = []
        total_hours = 0
        
        for item in scope_items:
            # Estimate hours based on item (simplified)
            item_hours = base["typical_hours"] / len(scope_items) if scope_items else base["typical_hours"]
            item_hours = round(item_hours * complexity_mult)
            total_hours += item_hours
            
            item_cost = round(item_hours * base["base_rate"] * timeline_mult, 2)
            
            line_items.append({
                "item": item,
                "estimated_hours": item_hours,
                "rate": base["base_rate"],
                "subtotal": item_cost
            })
        
        # Calculate totals
        subtotal = sum(item["subtotal"] for item in line_items)
        
        # Add project management (10%)
        pm_cost = round(subtotal * 0.10, 2)
        
        # Calculate total
        total = round(subtotal + pm_cost, 2)
        
        # Generate pricing options if requested
        pricing_options = []
        if include_options:
            pricing_options = [
                {
                    "option": "Basic",
                    "description": "Core deliverables only",
                    "price": round(total * 0.75, 2),
                    "includes": scope_items[:len(scope_items)//2 + 1] if len(scope_items) > 1 else scope_items,
                    "timeline_adjustment": "+2 weeks"
                },
                {
                    "option": "Standard",
                    "description": "Full scope as specified",
                    "price": total,
                    "includes": scope_items,
                    "timeline_adjustment": "As proposed"
                },
                {
                    "option": "Premium",
                    "description": "Enhanced deliverables with priority support",
                    "price": round(total * 1.35, 2),
                    "includes": scope_items + ["Priority support", "Extended warranty", "Quarterly reviews"],
                    "timeline_adjustment": "-1 week"
                }
            ]
        
        return {
            "project_type": project_type,
            "complexity": complexity,
            "timeline_preference": timeline_preference,
            "line_items": line_items,
            "summary": {
                "total_hours": total_hours,
                "average_rate": base["base_rate"],
                "subtotal": subtotal,
                "project_management": pm_cost,
                "total": total
            },
            "pricing_options": pricing_options,
            "assumptions": [
                "Pricing based on estimated scope complexity",
                "Assumes standard business hours availability",
                "Client to provide timely feedback and approvals",
                "Scope changes subject to change order process"
            ],
            "validity": "30 days",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def track_proposal(
        self,
        proposal_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """Track proposal status and deal progress"""
        supabase = get_supabase()
        
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        query = supabase.table("proposals") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat())
        
        if proposal_id:
            query = query.eq("id", proposal_id)
        if status_filter:
            query = query.eq("status", status_filter)
        
        result = query.order("created_at", desc=True).execute()
        proposals = result.data or []
        
        # Add mock proposals if none exist
        if not proposals:
            proposals = [
                {
                    "id": "prop_001",
                    "client_name": "Acme Corporation",
                    "project_title": "Digital Transformation Initiative",
                    "estimated_value": 75000.00,
                    "status": "sent",
                    "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                    "sent_at": (datetime.utcnow() - timedelta(days=4)).isoformat(),
                    "follow_up_date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "probability": 60
                },
                {
                    "id": "prop_002",
                    "client_name": "TechStart Inc",
                    "project_title": "Platform Development",
                    "estimated_value": 45000.00,
                    "status": "negotiating",
                    "created_at": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                    "sent_at": (datetime.utcnow() - timedelta(days=13)).isoformat(),
                    "follow_up_date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "probability": 75
                },
                {
                    "id": "prop_003",
                    "client_name": "Global Services Ltd",
                    "project_title": "System Integration",
                    "estimated_value": 120000.00,
                    "status": "draft",
                    "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                    "sent_at": None,
                    "follow_up_date": None,
                    "probability": 40
                },
                {
                    "id": "prop_004",
                    "client_name": "Metro Healthcare",
                    "project_title": "Compliance Automation",
                    "estimated_value": 55000.00,
                    "status": "won",
                    "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "sent_at": (datetime.utcnow() - timedelta(days=28)).isoformat(),
                    "won_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
                    "probability": 100
                },
                {
                    "id": "prop_005",
                    "client_name": "Retail Plus",
                    "project_title": "E-commerce Platform",
                    "estimated_value": 35000.00,
                    "status": "lost",
                    "created_at": (datetime.utcnow() - timedelta(days=45)).isoformat(),
                    "sent_at": (datetime.utcnow() - timedelta(days=44)).isoformat(),
                    "lost_at": (datetime.utcnow() - timedelta(days=20)).isoformat(),
                    "lost_reason": "Budget constraints",
                    "probability": 0
                }
            ]
        
        # Calculate pipeline metrics
        pipeline_value = sum(p.get("estimated_value", 0) for p in proposals if p.get("status") not in ["won", "lost"])
        weighted_pipeline = sum(
            p.get("estimated_value", 0) * (p.get("probability", 50) / 100) 
            for p in proposals if p.get("status") not in ["won", "lost"]
        )
        won_value = sum(p.get("estimated_value", 0) for p in proposals if p.get("status") == "won")
        lost_value = sum(p.get("estimated_value", 0) for p in proposals if p.get("status") == "lost")
        
        # Identify action items
        action_items = []
        for p in proposals:
            if p.get("status") == "draft":
                action_items.append({
                    "proposal_id": p["id"],
                    "client": p.get("client_name"),
                    "action": "Complete and send proposal",
                    "priority": "high"
                })
            elif p.get("status") == "sent":
                follow_up = p.get("follow_up_date")
                if follow_up:
                    follow_up_date = datetime.strptime(follow_up, "%Y-%m-%d").date()
                    if follow_up_date <= datetime.utcnow().date():
                        action_items.append({
                            "proposal_id": p["id"],
                            "client": p.get("client_name"),
                            "action": "Follow up - due today or overdue",
                            "priority": "high"
                        })
            elif p.get("status") == "negotiating":
                action_items.append({
                    "proposal_id": p["id"],
                    "client": p.get("client_name"),
                    "action": "Continue negotiation - push to close",
                    "priority": "medium"
                })
        
        # Calculate win rate
        completed = [p for p in proposals if p.get("status") in ["won", "lost"]]
        win_rate = (sum(1 for p in completed if p.get("status") == "won") / len(completed) * 100) if completed else 0
        
        return {
            "proposals": proposals,
            "pipeline_summary": {
                "total_proposals": len(proposals),
                "draft": sum(1 for p in proposals if p.get("status") == "draft"),
                "sent": sum(1 for p in proposals if p.get("status") == "sent"),
                "negotiating": sum(1 for p in proposals if p.get("status") == "negotiating"),
                "won": sum(1 for p in proposals if p.get("status") == "won"),
                "lost": sum(1 for p in proposals if p.get("status") == "lost")
            },
            "financial_summary": {
                "pipeline_value": pipeline_value,
                "weighted_pipeline": round(weighted_pipeline, 2),
                "won_value": won_value,
                "lost_value": lost_value,
                "win_rate_percent": round(win_rate, 1)
            },
            "action_items": action_items,
            "days_searched": days_back,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    async def analyze_win_rate(
        self,
        period_days: int = 180
    ) -> Dict[str, Any]:
        """Analyze win/loss patterns to improve proposal success"""
        supabase = get_supabase()
        
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        
        result = supabase.table("proposals") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .in_("status", ["won", "lost"]) \
            .execute()
        
        proposals = result.data or []
        
        # Add mock data if none exists
        if not proposals:
            proposals = [
                {"status": "won", "estimated_value": 55000, "project_title": "Compliance"},
                {"status": "won", "estimated_value": 30000, "project_title": "Training"},
                {"status": "won", "estimated_value": 42000, "project_title": "Development"},
                {"status": "lost", "estimated_value": 35000, "project_title": "E-commerce", "lost_reason": "Budget constraints"},
                {"status": "lost", "estimated_value": 80000, "project_title": "Platform", "lost_reason": "Went with competitor"},
                {"status": "lost", "estimated_value": 25000, "project_title": "Support", "lost_reason": "Project cancelled"},
            ]
        
        won = [p for p in proposals if p.get("status") == "won"]
        lost = [p for p in proposals if p.get("status") == "lost"]
        
        # Calculate metrics
        total_won_value = sum(p.get("estimated_value", 0) for p in won)
        total_lost_value = sum(p.get("estimated_value", 0) for p in lost)
        avg_won_value = total_won_value / len(won) if won else 0
        avg_lost_value = total_lost_value / len(lost) if lost else 0
        
        # Analyze loss reasons
        loss_reasons = {}
        for p in lost:
            reason = p.get("lost_reason", "Unknown")
            loss_reasons[reason] = loss_reasons.get(reason, 0) + 1
        
        # Generate insights
        insights = []
        win_rate = len(won) / len(proposals) * 100 if proposals else 0
        
        if win_rate >= 60:
            insights.append("Strong win rate - maintain current proposal strategy")
        elif win_rate >= 40:
            insights.append("Moderate win rate - review lost proposal feedback for improvements")
        else:
            insights.append("Win rate needs improvement - consider proposal training or pricing review")
        
        if avg_won_value < avg_lost_value:
            insights.append("Higher-value deals more likely to be lost - consider value justification improvements")
        
        if "Budget constraints" in loss_reasons:
            insights.append("Budget is a common loss reason - consider offering tiered pricing options")
        
        if "Went with competitor" in loss_reasons:
            insights.append("Lost to competitors - strengthen differentiation in proposals")
        
        # Generate recommendations
        recommendations = [
            "Follow up within 48 hours of sending proposals",
            "Include case studies relevant to client industry",
            "Offer multiple pricing tiers for flexibility",
            "Address common objections proactively in proposals",
            "Request feedback on all lost proposals for continuous improvement"
        ]
        
        return {
            "period_days": period_days,
            "metrics": {
                "total_proposals": len(proposals),
                "won": len(won),
                "lost": len(lost),
                "win_rate_percent": round(win_rate, 1),
                "total_won_value": total_won_value,
                "total_lost_value": total_lost_value,
                "average_won_value": round(avg_won_value, 2),
                "average_lost_value": round(avg_lost_value, 2)
            },
            "loss_analysis": {
                "reasons": loss_reasons,
                "top_reason": max(loss_reasons, key=loss_reasons.get) if loss_reasons else "N/A"
            },
            "insights": insights,
            "recommendations": recommendations,
            "analyzed_at": datetime.utcnow().isoformat()
        }
