from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx

from app.core.database import get_supabase


class VendorTools:
    """Tools for vendor contract management and negotiation"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def analyze_contracts(
        self,
        vendor_name: Optional[str] = None,
        category: Optional[str] = None,
        expiring_within_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze vendor contracts and extract key terms"""
        supabase = get_supabase()
        
        query = supabase.table("vendor_contracts") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .eq("status", "active")
        
        if vendor_name:
            query = query.ilike("vendor_name", f"%{vendor_name}%")
        if category:
            query = query.eq("category", category)
        
        result = query.order("renewal_date", desc=False).execute()
        contracts = result.data or []
        
        # Add mock contracts if none exist
        if not contracts:
            contracts = [
                {
                    "id": "contract_001",
                    "vendor_name": "CloudHost Pro",
                    "category": "software",
                    "description": "Cloud hosting and infrastructure",
                    "monthly_cost": 2500.00,
                    "annual_cost": 30000.00,
                    "contract_start": (datetime.utcnow() - timedelta(days=300)).strftime("%Y-%m-%d"),
                    "renewal_date": (datetime.utcnow() + timedelta(days=65)).strftime("%Y-%m-%d"),
                    "term_months": 12,
                    "auto_renew": True,
                    "cancellation_notice_days": 30,
                    "payment_terms": "Net 30",
                    "key_terms": ["99.9% uptime SLA", "24/7 support", "Data backup included"],
                    "status": "active"
                },
                {
                    "id": "contract_002",
                    "vendor_name": "Office Supplies Direct",
                    "category": "supplies",
                    "description": "Office supplies and equipment",
                    "monthly_cost": 800.00,
                    "annual_cost": 9600.00,
                    "contract_start": (datetime.utcnow() - timedelta(days=180)).strftime("%Y-%m-%d"),
                    "renewal_date": (datetime.utcnow() + timedelta(days=185)).strftime("%Y-%m-%d"),
                    "term_months": 12,
                    "auto_renew": False,
                    "cancellation_notice_days": 60,
                    "payment_terms": "Net 15",
                    "key_terms": ["Free delivery over $100", "10% volume discount", "30-day returns"],
                    "status": "active"
                },
                {
                    "id": "contract_003",
                    "vendor_name": "SecureIT Solutions",
                    "category": "software",
                    "description": "Cybersecurity and antivirus",
                    "monthly_cost": 450.00,
                    "annual_cost": 5400.00,
                    "contract_start": (datetime.utcnow() - timedelta(days=100)).strftime("%Y-%m-%d"),
                    "renewal_date": (datetime.utcnow() + timedelta(days=265)).strftime("%Y-%m-%d"),
                    "term_months": 12,
                    "auto_renew": True,
                    "cancellation_notice_days": 45,
                    "payment_terms": "Annual prepay",
                    "key_terms": ["Unlimited devices", "Real-time threat protection", "Compliance reporting"],
                    "status": "active"
                },
                {
                    "id": "contract_004",
                    "vendor_name": "Marketing Masters",
                    "category": "services",
                    "description": "Digital marketing services",
                    "monthly_cost": 3500.00,
                    "annual_cost": 42000.00,
                    "contract_start": (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d"),
                    "renewal_date": (datetime.utcnow() + timedelta(days=305)).strftime("%Y-%m-%d"),
                    "term_months": 12,
                    "auto_renew": False,
                    "cancellation_notice_days": 30,
                    "payment_terms": "Net 30",
                    "key_terms": ["Monthly reporting", "SEO optimization", "Social media management"],
                    "status": "active"
                },
                {
                    "id": "contract_005",
                    "vendor_name": "QuickShip Logistics",
                    "category": "logistics",
                    "description": "Shipping and fulfillment",
                    "monthly_cost": 1200.00,
                    "annual_cost": 14400.00,
                    "contract_start": (datetime.utcnow() - timedelta(days=200)).strftime("%Y-%m-%d"),
                    "renewal_date": (datetime.utcnow() + timedelta(days=25)).strftime("%Y-%m-%d"),
                    "term_months": 12,
                    "auto_renew": True,
                    "cancellation_notice_days": 60,
                    "payment_terms": "Net 15",
                    "key_terms": ["Next-day shipping available", "Package tracking", "Insurance included"],
                    "status": "active"
                }
            ]
        
        # Filter by expiring within days if specified
        if expiring_within_days:
            cutoff = datetime.utcnow() + timedelta(days=expiring_within_days)
            contracts = [
                c for c in contracts 
                if datetime.strptime(c["renewal_date"], "%Y-%m-%d") <= cutoff
            ]
        
        # Add days until renewal
        for contract in contracts:
            renewal = datetime.strptime(contract["renewal_date"], "%Y-%m-%d")
            contract["days_until_renewal"] = (renewal - datetime.utcnow()).days
        
        # Calculate totals
        total_monthly = sum(c.get("monthly_cost", 0) for c in contracts)
        total_annual = sum(c.get("annual_cost", 0) for c in contracts)
        
        return {
            "contracts": contracts,
            "total_contracts": len(contracts),
            "total_monthly_spend": total_monthly,
            "total_annual_spend": total_annual,
            "categories": list(set(c.get("category", "other") for c in contracts)),
            "expiring_soon": sum(1 for c in contracts if c.get("days_until_renewal", 999) <= 60),
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    async def benchmark_pricing(
        self,
        vendor_name: str,
        category: str,
        current_price: float,
        service_description: str = ""
    ) -> Dict[str, Any]:
        """Benchmark vendor pricing against market rates"""
        
        # In production, this would call pricing APIs or use ML models
        # For now, return mock benchmark data
        market_data = {
            "software": {
                "cloud_hosting": {"low": 0.70, "median": 1.0, "high": 1.35},
                "security": {"low": 0.75, "median": 1.0, "high": 1.25},
                "productivity": {"low": 0.80, "median": 1.0, "high": 1.20},
                "default": {"low": 0.75, "median": 1.0, "high": 1.30}
            },
            "services": {
                "marketing": {"low": 0.65, "median": 1.0, "high": 1.40},
                "consulting": {"low": 0.70, "median": 1.0, "high": 1.50},
                "default": {"low": 0.70, "median": 1.0, "high": 1.35}
            },
            "supplies": {
                "default": {"low": 0.80, "median": 1.0, "high": 1.15}
            },
            "logistics": {
                "default": {"low": 0.85, "median": 1.0, "high": 1.20}
            }
        }
        
        cat_data = market_data.get(category, market_data.get("services", {}))
        
        # Try to match subcategory from service description
        subcategory = "default"
        desc_lower = service_description.lower()
        for key in cat_data.keys():
            if key != "default" and key in desc_lower:
                subcategory = key
                break
        
        multipliers = cat_data.get(subcategory, cat_data.get("default", {"low": 0.75, "median": 1.0, "high": 1.30}))
        
        # Assume current price is close to median, calculate ranges
        estimated_median = current_price
        market_low = round(estimated_median * multipliers["low"], 2)
        market_high = round(estimated_median * multipliers["high"], 2)
        
        # Determine price position
        position_ratio = 1.0  # Assume at median
        if current_price < market_low:
            position = "below_market"
            savings_potential = 0
            position_ratio = current_price / market_low
        elif current_price > estimated_median * 1.1:
            position = "above_market"
            savings_potential = round(current_price - estimated_median, 2)
            position_ratio = current_price / estimated_median
        else:
            position = "at_market"
            savings_potential = round(current_price * 0.05, 2)  # 5% potential through negotiation
        
        # Generate negotiation leverage points
        leverage_points = []
        if position == "above_market":
            leverage_points.append(f"Current pricing is {round((position_ratio - 1) * 100)}% above market median")
            leverage_points.append("Request price match to market rates")
        leverage_points.append("Multi-year commitment for volume discount")
        leverage_points.append("Bundle services for package pricing")
        leverage_points.append("Request loyalty discount for renewal")
        
        supabase = get_supabase()
        supabase.table("pricing_benchmarks").insert({
            "user_id": self.user_id,
            "vendor_name": vendor_name,
            "category": category,
            "current_price": current_price,
            "market_low": market_low,
            "market_median": estimated_median,
            "market_high": market_high,
            "position": position,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "vendor_name": vendor_name,
            "category": category,
            "current_price": current_price,
            "market_analysis": {
                "low": market_low,
                "median": estimated_median,
                "high": market_high
            },
            "position": position,
            "savings_potential": savings_potential,
            "annual_savings_potential": round(savings_potential * 12, 2),
            "leverage_points": leverage_points,
            "confidence": "medium",
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def identify_savings(
        self,
        min_savings_threshold: float = 100.0
    ) -> Dict[str, Any]:
        """Identify savings opportunities across all vendor relationships"""
        supabase = get_supabase()
        
        # Get all active contracts
        contracts_result = await self.analyze_contracts()
        contracts = contracts_result.get("contracts", [])
        
        opportunities = []
        total_potential_savings = 0
        
        for contract in contracts:
            # Analyze each contract for savings
            monthly_cost = contract.get("monthly_cost", 0)
            category = contract.get("category", "other")
            days_until_renewal = contract.get("days_until_renewal", 365)
            auto_renew = contract.get("auto_renew", False)
            
            opportunity = {
                "vendor_name": contract.get("vendor_name"),
                "contract_id": contract.get("id"),
                "current_monthly": monthly_cost,
                "current_annual": contract.get("annual_cost", monthly_cost * 12),
                "opportunity_type": [],
                "potential_monthly_savings": 0,
                "potential_annual_savings": 0,
                "priority": "low",
                "recommended_actions": []
            }
            
            # Check for renewal negotiation opportunity
            if days_until_renewal <= 90:
                opportunity["opportunity_type"].append("renewal_negotiation")
                estimated_savings = monthly_cost * 0.10  # 10% potential
                opportunity["potential_monthly_savings"] += estimated_savings
                opportunity["recommended_actions"].append(
                    f"Contract renews in {days_until_renewal} days - initiate renewal negotiation"
                )
                if auto_renew:
                    opportunity["recommended_actions"].append(
                        f"Auto-renew is ON - disable to maintain negotiating leverage"
                    )
                opportunity["priority"] = "high" if days_until_renewal <= 30 else "medium"
            
            # Check for consolidation opportunity (multiple vendors same category)
            same_category = [c for c in contracts if c.get("category") == category and c.get("id") != contract.get("id")]
            if same_category:
                opportunity["opportunity_type"].append("consolidation")
                opportunity["recommended_actions"].append(
                    f"Consider consolidating with {len(same_category)} other {category} vendors"
                )
            
            # Check for volume discount opportunity
            if monthly_cost >= 1000:
                opportunity["opportunity_type"].append("volume_discount")
                volume_savings = monthly_cost * 0.05
                opportunity["potential_monthly_savings"] += volume_savings
                opportunity["recommended_actions"].append(
                    "Request volume discount based on spend level"
                )
            
            # Check for payment terms optimization
            if contract.get("payment_terms") == "Net 30":
                opportunity["opportunity_type"].append("payment_optimization")
                opportunity["recommended_actions"].append(
                    "Negotiate early payment discount (2% for Net 10)"
                )
            
            # Calculate annual savings
            opportunity["potential_annual_savings"] = round(opportunity["potential_monthly_savings"] * 12, 2)
            opportunity["potential_monthly_savings"] = round(opportunity["potential_monthly_savings"], 2)
            
            # Only include if meets threshold
            if opportunity["potential_annual_savings"] >= min_savings_threshold or opportunity["priority"] in ["high", "medium"]:
                opportunities.append(opportunity)
                total_potential_savings += opportunity["potential_annual_savings"]
        
        # Sort by priority and savings potential
        priority_order = {"high": 0, "medium": 1, "low": 2}
        opportunities.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["potential_annual_savings"]))
        
        # Log savings analysis
        supabase.table("savings_analyses").insert({
            "user_id": self.user_id,
            "total_opportunities": len(opportunities),
            "total_potential_savings": total_potential_savings,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "opportunities": opportunities,
            "summary": {
                "total_opportunities": len(opportunities),
                "high_priority": sum(1 for o in opportunities if o["priority"] == "high"),
                "medium_priority": sum(1 for o in opportunities if o["priority"] == "medium"),
                "total_potential_annual_savings": round(total_potential_savings, 2)
            },
            "top_actions": [o["recommended_actions"][0] for o in opportunities[:3] if o["recommended_actions"]],
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def draft_negotiation(
        self,
        vendor_name: str,
        negotiation_type: str,
        current_terms: str,
        desired_outcome: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Draft a negotiation email or script for vendor discussions"""
        supabase = get_supabase()
        
        # Define negotiation templates based on type
        templates = {
            "renewal": {
                "subject": f"Contract Renewal Discussion - {vendor_name}",
                "opening": f"I hope this message finds you well. As our contract with {vendor_name} approaches renewal, I wanted to reach out to discuss our continued partnership.",
                "body_points": [
                    "We have valued our relationship and the services provided",
                    "As we review our vendor relationships, we're evaluating options",
                    "We'd like to discuss terms that reflect our ongoing commitment"
                ],
                "ask": "We're seeking improved pricing that reflects our loyalty and the current market conditions.",
                "closing": "I'm confident we can find terms that work for both parties. When would be a good time to discuss?"
            },
            "price_reduction": {
                "subject": f"Pricing Discussion - {vendor_name} Account",
                "opening": f"Thank you for your continued partnership. I'm reaching out to discuss our current pricing arrangement with {vendor_name}.",
                "body_points": [
                    "We've conducted a market analysis of comparable services",
                    "Our research indicates competitive options at lower price points",
                    "We prefer to continue our relationship with you"
                ],
                "ask": "We're requesting a pricing adjustment to align with current market rates.",
                "closing": "We value our relationship and hope to reach a mutually beneficial agreement. Please let me know your availability to discuss."
            },
            "service_upgrade": {
                "subject": f"Service Enhancement Discussion - {vendor_name}",
                "opening": f"I wanted to reach out regarding potential enhancements to our service agreement with {vendor_name}.",
                "body_points": [
                    "Our business needs have evolved since we began our partnership",
                    "We're interested in additional capabilities",
                    "We'd like to explore options within our current budget"
                ],
                "ask": "We're looking to add services while maintaining our current spend level.",
                "closing": "I'd appreciate the opportunity to explore how we can grow our partnership. What times work for a call?"
            },
            "cancellation_prevention": {
                "subject": f"Account Review - {vendor_name}",
                "opening": f"I'm writing to discuss our current arrangement with {vendor_name} and explore our options going forward.",
                "body_points": [
                    "We've been reviewing our vendor relationships and budget allocation",
                    "We need to ensure we're getting maximum value from our investments",
                    "We're evaluating whether to continue or explore alternatives"
                ],
                "ask": "Before making any decisions, we wanted to discuss what options might be available.",
                "closing": "We're open to discussing how we might continue our relationship under revised terms. Please advise on next steps."
            }
        }
        
        template = templates.get(negotiation_type, templates["renewal"])
        
        # Build the draft
        if tone == "firm":
            template["opening"] = template["opening"].replace("I hope this message finds you well. ", "")
            template["closing"] = "Please respond by [DATE] with your best offer."
        elif tone == "friendly":
            template["opening"] = f"I hope you're doing well! " + template["opening"]
        
        draft = {
            "subject": template["subject"],
            "body": f"""Dear {vendor_name} Team,

{template["opening"]}

Current Terms: {current_terms}

{chr(10).join(f"• {point}" for point in template["body_points"])}

{template["ask"]}

Desired Outcome: {desired_outcome}

{template["closing"]}

Best regards,
[Your Name]
[Your Title]
[Company Name]"""
        }
        
        # Generate talking points for calls
        talking_points = [
            f"Open by acknowledging the partnership with {vendor_name}",
            "Reference your tenure as a customer",
            "Mention you've been reviewing vendor relationships",
            f"State your goal: {desired_outcome}",
            "Be prepared to discuss alternatives you've researched",
            "Ask what flexibility they have on pricing/terms",
            "If needed, ask to speak with a manager or retention team",
            "Get any agreements in writing before ending the call"
        ]
        
        # Log the draft
        supabase.table("negotiation_drafts").insert({
            "user_id": self.user_id,
            "vendor_name": vendor_name,
            "negotiation_type": negotiation_type,
            "tone": tone,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "vendor_name": vendor_name,
            "negotiation_type": negotiation_type,
            "email_draft": draft,
            "talking_points": talking_points,
            "tips": [
                "Send emails Tuesday-Thursday for best response rates",
                "Follow up if no response within 3 business days",
                "Document all communications for reference",
                "Be prepared to walk away if terms aren't met"
            ],
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def track_renewals(
        self,
        days_ahead: int = 90
    ) -> Dict[str, Any]:
        """Track upcoming contract renewals and required actions"""
        supabase = get_supabase()
        
        contracts_result = await self.analyze_contracts(expiring_within_days=days_ahead)
        contracts = contracts_result.get("contracts", [])
        
        renewals = []
        for contract in contracts:
            days_until = contract.get("days_until_renewal", 0)
            notice_days = contract.get("cancellation_notice_days", 30)
            
            # Determine status and urgency
            if days_until <= notice_days:
                status = "action_required"
                urgency = "critical"
            elif days_until <= notice_days + 14:
                status = "attention_needed"
                urgency = "high"
            elif days_until <= 60:
                status = "upcoming"
                urgency = "medium"
            else:
                status = "scheduled"
                urgency = "low"
            
            # Calculate key dates
            notice_deadline = datetime.strptime(contract["renewal_date"], "%Y-%m-%d") - timedelta(days=notice_days)
            
            renewal_entry = {
                "contract_id": contract.get("id"),
                "vendor_name": contract.get("vendor_name"),
                "category": contract.get("category"),
                "renewal_date": contract.get("renewal_date"),
                "days_until_renewal": days_until,
                "cancellation_notice_days": notice_days,
                "notice_deadline": notice_deadline.strftime("%Y-%m-%d"),
                "days_until_notice_deadline": (notice_deadline - datetime.utcnow()).days,
                "auto_renew": contract.get("auto_renew", False),
                "monthly_cost": contract.get("monthly_cost"),
                "annual_cost": contract.get("annual_cost"),
                "status": status,
                "urgency": urgency,
                "recommended_action": self._get_renewal_recommendation(status, contract)
            }
            renewals.append(renewal_entry)
        
        # Sort by urgency
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        renewals.sort(key=lambda x: (urgency_order.get(x["urgency"], 4), x["days_until_renewal"]))
        
        return {
            "renewals": renewals,
            "summary": {
                "total_renewals": len(renewals),
                "critical": sum(1 for r in renewals if r["urgency"] == "critical"),
                "high": sum(1 for r in renewals if r["urgency"] == "high"),
                "medium": sum(1 for r in renewals if r["urgency"] == "medium"),
                "total_annual_value": sum(r.get("annual_cost", 0) for r in renewals)
            },
            "days_ahead_searched": days_ahead,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    def _get_renewal_recommendation(self, status: str, contract: Dict) -> str:
        """Get recommended action based on renewal status"""
        vendor = contract.get("vendor_name", "vendor")
        
        recommendations = {
            "action_required": f"URGENT: Contact {vendor} immediately to negotiate or cancel before deadline",
            "attention_needed": f"Schedule negotiation call with {vendor} this week",
            "upcoming": f"Begin preparing negotiation strategy for {vendor}",
            "scheduled": f"Add {vendor} renewal to calendar for future planning"
        }
        return recommendations.get(status, "Review contract terms")
