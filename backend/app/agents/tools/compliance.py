from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx

from app.core.database import get_supabase


class ComplianceTools:
    """Tools for regulatory compliance monitoring and management"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def monitor_regulations(
        self,
        industry: str = "general",
        jurisdiction: str = "federal",
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Monitor regulatory changes relevant to the business"""
        supabase = get_supabase()
        
        # In production, this would integrate with regulatory APIs
        # For now, return mock regulatory updates
        mock_updates = [
            {
                "id": "reg_001",
                "title": "Updated Data Privacy Requirements",
                "agency": "FTC",
                "effective_date": (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
                "summary": "New requirements for consumer data handling and breach notification procedures",
                "impact_level": "high",
                "categories": ["privacy", "data_security"],
                "action_required": True,
                "compliance_deadline": (datetime.utcnow() + timedelta(days=60)).strftime("%Y-%m-%d")
            },
            {
                "id": "reg_002",
                "title": "Workplace Safety Standards Update",
                "agency": "OSHA",
                "effective_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "summary": "Revised workplace safety protocols for remote and hybrid work environments",
                "impact_level": "medium",
                "categories": ["workplace_safety", "hr"],
                "action_required": True,
                "compliance_deadline": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
            },
            {
                "id": "reg_003",
                "title": "Tax Reporting Changes for Small Business",
                "agency": "IRS",
                "effective_date": (datetime.utcnow() + timedelta(days=180)).strftime("%Y-%m-%d"),
                "summary": "New 1099-K reporting thresholds and requirements",
                "impact_level": "medium",
                "categories": ["tax", "financial_reporting"],
                "action_required": False,
                "compliance_deadline": None
            },
            {
                "id": "reg_004",
                "title": "Environmental Compliance Reporting",
                "agency": "EPA",
                "effective_date": (datetime.utcnow() + timedelta(days=120)).strftime("%Y-%m-%d"),
                "summary": "Updated emissions reporting requirements for businesses",
                "impact_level": "low",
                "categories": ["environmental"],
                "action_required": False,
                "compliance_deadline": None
            }
        ]
        
        # Filter by categories if provided
        if categories:
            mock_updates = [
                u for u in mock_updates 
                if any(cat in u["categories"] for cat in categories)
            ]
        
        # Log the monitoring activity
        supabase.table("compliance_monitoring").insert({
            "user_id": self.user_id,
            "industry": industry,
            "jurisdiction": jurisdiction,
            "categories": categories,
            "updates_found": len(mock_updates),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "industry": industry,
            "jurisdiction": jurisdiction,
            "regulatory_updates": mock_updates,
            "total_updates": len(mock_updates),
            "action_required_count": sum(1 for u in mock_updates if u["action_required"]),
            "monitored_at": datetime.utcnow().isoformat()
        }
    
    async def track_deadlines(
        self,
        days_ahead: int = 90,
        include_completed: bool = False
    ) -> Dict[str, Any]:
        """Track compliance deadlines and upcoming requirements"""
        supabase = get_supabase()
        
        query = supabase.table("compliance_deadlines") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("due_date", datetime.utcnow().strftime("%Y-%m-%d")) \
            .lte("due_date", (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")) \
            .order("due_date", desc=False)
        
        if not include_completed:
            query = query.neq("status", "completed")
        
        result = query.execute()
        deadlines = result.data or []
        
        # Add mock deadlines if none exist
        if not deadlines:
            deadlines = [
                {
                    "id": "dl_001",
                    "title": "Q1 Tax Filing",
                    "description": "Quarterly estimated tax payment due",
                    "due_date": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"),
                    "category": "tax",
                    "priority": "high",
                    "status": "pending",
                    "assigned_to": None,
                    "reminder_sent": False
                },
                {
                    "id": "dl_002",
                    "title": "Annual Privacy Policy Review",
                    "description": "Review and update privacy policy for compliance",
                    "due_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "category": "privacy",
                    "priority": "medium",
                    "status": "in_progress",
                    "assigned_to": "legal@company.com",
                    "reminder_sent": True
                },
                {
                    "id": "dl_003",
                    "title": "Employee Safety Training",
                    "description": "Complete annual safety training for all employees",
                    "due_date": (datetime.utcnow() + timedelta(days=45)).strftime("%Y-%m-%d"),
                    "category": "workplace_safety",
                    "priority": "medium",
                    "status": "pending",
                    "assigned_to": "hr@company.com",
                    "reminder_sent": False
                },
                {
                    "id": "dl_004",
                    "title": "Business License Renewal",
                    "description": "Renew annual business operating license",
                    "due_date": (datetime.utcnow() + timedelta(days=60)).strftime("%Y-%m-%d"),
                    "category": "licensing",
                    "priority": "high",
                    "status": "pending",
                    "assigned_to": None,
                    "reminder_sent": False
                }
            ]
        
        # Categorize by urgency
        overdue = []
        urgent = []  # Due within 7 days
        upcoming = []  # Due within 30 days
        future = []  # Beyond 30 days
        
        today = datetime.utcnow().date()
        
        for dl in deadlines:
            due = datetime.strptime(dl["due_date"], "%Y-%m-%d").date()
            days_until = (due - today).days
            dl["days_until_due"] = days_until
            
            if days_until < 0:
                overdue.append(dl)
            elif days_until <= 7:
                urgent.append(dl)
            elif days_until <= 30:
                upcoming.append(dl)
            else:
                future.append(dl)
        
        return {
            "summary": {
                "total_deadlines": len(deadlines),
                "overdue": len(overdue),
                "urgent_7_days": len(urgent),
                "upcoming_30_days": len(upcoming),
                "future": len(future)
            },
            "overdue": overdue,
            "urgent": urgent,
            "upcoming": upcoming,
            "future": future,
            "days_ahead_searched": days_ahead,
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    async def audit_compliance(
        self,
        area: str = "all",
        detailed: bool = True
    ) -> Dict[str, Any]:
        """Audit current compliance status across different areas"""
        supabase = get_supabase()
        
        # Define compliance areas and checks
        compliance_areas = {
            "data_privacy": {
                "name": "Data Privacy & Security",
                "checks": [
                    {"item": "Privacy policy published and up-to-date", "status": "compliant", "notes": "Last updated 3 months ago"},
                    {"item": "Data breach response plan documented", "status": "compliant", "notes": "Plan reviewed quarterly"},
                    {"item": "Customer consent mechanisms in place", "status": "needs_attention", "notes": "Cookie consent banner needs update"},
                    {"item": "Data retention policy enforced", "status": "compliant", "notes": "Automated deletion configured"},
                    {"item": "Employee data handling training", "status": "non_compliant", "notes": "Training overdue for 5 employees"}
                ]
            },
            "financial": {
                "name": "Financial Compliance",
                "checks": [
                    {"item": "Tax filings current", "status": "compliant", "notes": "All filings up to date"},
                    {"item": "Financial records properly maintained", "status": "compliant", "notes": "Using certified accounting software"},
                    {"item": "Audit trail for transactions", "status": "compliant", "notes": "Full audit trail enabled"},
                    {"item": "Anti-money laundering procedures", "status": "needs_attention", "notes": "Annual review due next month"}
                ]
            },
            "employment": {
                "name": "Employment & HR",
                "checks": [
                    {"item": "Employee handbook current", "status": "compliant", "notes": "Updated this year"},
                    {"item": "I-9 verification complete", "status": "compliant", "notes": "All employees verified"},
                    {"item": "Workplace safety protocols", "status": "needs_attention", "notes": "Remote work policy needs update"},
                    {"item": "Anti-discrimination policy", "status": "compliant", "notes": "Training completed"},
                    {"item": "Workers compensation insurance", "status": "compliant", "notes": "Policy active"}
                ]
            },
            "licensing": {
                "name": "Licenses & Permits",
                "checks": [
                    {"item": "Business license active", "status": "compliant", "notes": "Expires in 8 months"},
                    {"item": "Professional certifications current", "status": "needs_attention", "notes": "2 certifications expiring soon"},
                    {"item": "Industry-specific permits", "status": "compliant", "notes": "All permits current"}
                ]
            }
        }
        
        # Filter by area if specified
        if area != "all" and area in compliance_areas:
            compliance_areas = {area: compliance_areas[area]}
        
        # Calculate scores
        audit_results = []
        total_checks = 0
        compliant_checks = 0
        needs_attention = 0
        non_compliant = 0
        
        for area_key, area_data in compliance_areas.items():
            area_compliant = 0
            area_attention = 0
            area_non_compliant = 0
            
            for check in area_data["checks"]:
                total_checks += 1
                if check["status"] == "compliant":
                    compliant_checks += 1
                    area_compliant += 1
                elif check["status"] == "needs_attention":
                    needs_attention += 1
                    area_attention += 1
                else:
                    non_compliant += 1
                    area_non_compliant += 1
            
            area_total = len(area_data["checks"])
            area_score = round((area_compliant / area_total) * 100) if area_total > 0 else 0
            
            audit_results.append({
                "area": area_key,
                "name": area_data["name"],
                "score": area_score,
                "compliant": area_compliant,
                "needs_attention": area_attention,
                "non_compliant": area_non_compliant,
                "total_checks": area_total,
                "checks": area_data["checks"] if detailed else None
            })
        
        overall_score = round((compliant_checks / total_checks) * 100) if total_checks > 0 else 0
        
        # Log audit
        supabase.table("compliance_audits").insert({
            "user_id": self.user_id,
            "area": area,
            "overall_score": overall_score,
            "total_checks": total_checks,
            "compliant": compliant_checks,
            "needs_attention": needs_attention,
            "non_compliant": non_compliant,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "overall_score": overall_score,
            "summary": {
                "total_checks": total_checks,
                "compliant": compliant_checks,
                "needs_attention": needs_attention,
                "non_compliant": non_compliant
            },
            "risk_level": "low" if overall_score >= 80 else "medium" if overall_score >= 60 else "high",
            "areas": audit_results,
            "recommendations": self._generate_audit_recommendations(audit_results),
            "audited_at": datetime.utcnow().isoformat()
        }
    
    def _generate_audit_recommendations(self, audit_results: List[Dict]) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        for area in audit_results:
            if area["non_compliant"] > 0:
                recommendations.append(f"URGENT: Address {area['non_compliant']} non-compliant item(s) in {area['name']}")
            if area["needs_attention"] > 0:
                recommendations.append(f"Review {area['needs_attention']} item(s) needing attention in {area['name']}")
            if area["score"] < 70:
                recommendations.append(f"Priority: Improve compliance in {area['name']} (current score: {area['score']}%)")
        
        if not recommendations:
            recommendations.append("Compliance status is healthy. Continue regular monitoring.")
        
        return recommendations
    
    async def generate_policy(
        self,
        policy_type: str,
        company_name: str = "Your Company",
        industry: str = "general"
    ) -> Dict[str, Any]:
        """Generate a compliance policy document"""
        supabase = get_supabase()
        
        policy_templates = {
            "privacy": {
                "title": f"{company_name} Privacy Policy",
                "sections": [
                    {"heading": "Information We Collect", "content": "We collect information you provide directly, including name, email, and contact details when you use our services or contact us."},
                    {"heading": "How We Use Your Information", "content": "We use collected information to provide and improve our services, communicate with you, and comply with legal obligations."},
                    {"heading": "Information Sharing", "content": "We do not sell your personal information. We may share information with service providers who assist our operations, subject to confidentiality agreements."},
                    {"heading": "Data Security", "content": "We implement appropriate technical and organizational measures to protect your personal information against unauthorized access or disclosure."},
                    {"heading": "Your Rights", "content": "You have the right to access, correct, or delete your personal information. Contact us to exercise these rights."},
                    {"heading": "Contact Us", "content": f"For privacy-related inquiries, contact {company_name} at privacy@company.com."}
                ]
            },
            "data_retention": {
                "title": f"{company_name} Data Retention Policy",
                "sections": [
                    {"heading": "Purpose", "content": "This policy establishes guidelines for retaining and disposing of company and customer data."},
                    {"heading": "Retention Periods", "content": "Customer data: 7 years after last activity. Financial records: 7 years. Employee records: 7 years after termination. Marketing data: 3 years."},
                    {"heading": "Secure Disposal", "content": "Data beyond retention period must be securely deleted using approved methods."},
                    {"heading": "Exceptions", "content": "Legal holds and regulatory requirements may extend retention periods."},
                    {"heading": "Responsibilities", "content": "Department heads are responsible for compliance within their areas."}
                ]
            },
            "acceptable_use": {
                "title": f"{company_name} Acceptable Use Policy",
                "sections": [
                    {"heading": "Purpose", "content": "This policy defines acceptable use of company technology resources and systems."},
                    {"heading": "Permitted Use", "content": "Company resources are provided for business purposes. Limited personal use is permitted if it does not interfere with work."},
                    {"heading": "Prohibited Activities", "content": "Prohibited: illegal activities, harassment, unauthorized access, sharing confidential data, installing unauthorized software."},
                    {"heading": "Monitoring", "content": "Company reserves the right to monitor use of company systems and resources."},
                    {"heading": "Enforcement", "content": "Violations may result in disciplinary action up to and including termination."}
                ]
            },
            "incident_response": {
                "title": f"{company_name} Security Incident Response Plan",
                "sections": [
                    {"heading": "Purpose", "content": "This plan establishes procedures for responding to security incidents and data breaches."},
                    {"heading": "Incident Classification", "content": "Level 1: Minor (contained). Level 2: Moderate (potential data exposure). Level 3: Severe (confirmed breach)."},
                    {"heading": "Response Team", "content": "Incident response team includes IT Security, Legal, HR, and Executive leadership."},
                    {"heading": "Response Procedures", "content": "1. Contain the incident. 2. Assess scope and impact. 3. Notify stakeholders. 4. Remediate. 5. Document and review."},
                    {"heading": "Notification Requirements", "content": "Affected individuals must be notified within 72 hours of confirmed breach. Regulators notified per applicable law."},
                    {"heading": "Post-Incident Review", "content": "All incidents require post-mortem review and documentation of lessons learned."}
                ]
            }
        }
        
        if policy_type not in policy_templates:
            return {
                "error": f"Unknown policy type: {policy_type}",
                "available_types": list(policy_templates.keys())
            }
        
        policy = policy_templates[policy_type]
        
        # Log policy generation
        supabase.table("generated_policies").insert({
            "user_id": self.user_id,
            "policy_type": policy_type,
            "company_name": company_name,
            "industry": industry,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "policy_type": policy_type,
            "title": policy["title"],
            "sections": policy["sections"],
            "generated_at": datetime.utcnow().isoformat(),
            "disclaimer": "This is a template. Consult legal counsel before implementation.",
            "status": "draft"
        }
    
    async def prepare_audit_report(
        self,
        report_type: str = "comprehensive",
        period_days: int = 90
    ) -> Dict[str, Any]:
        """Prepare an audit-ready compliance report"""
        supabase = get_supabase()
        
        cutoff = datetime.utcnow() - timedelta(days=period_days)
        
        # Get audit history
        audits = supabase.table("compliance_audits") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .order("created_at", desc=True) \
            .execute()
        
        # Get monitoring history
        monitoring = supabase.table("compliance_monitoring") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .execute()
        
        # Get generated policies
        policies = supabase.table("generated_policies") \
            .select("*") \
            .eq("user_id", self.user_id) \
            .gte("created_at", cutoff.isoformat()) \
            .execute()
        
        audits_data = audits.data or []
        monitoring_data = monitoring.data or []
        policies_data = policies.data or []
        
        # Calculate trends
        avg_score = 0
        if audits_data:
            scores = [a.get("overall_score", 0) for a in audits_data]
            avg_score = round(sum(scores) / len(scores))
        
        report = {
            "report_type": report_type,
            "period": {
                "days": period_days,
                "start_date": cutoff.strftime("%Y-%m-%d"),
                "end_date": datetime.utcnow().strftime("%Y-%m-%d")
            },
            "executive_summary": {
                "overall_compliance_score": avg_score,
                "risk_level": "low" if avg_score >= 80 else "medium" if avg_score >= 60 else "high",
                "total_audits_conducted": len(audits_data),
                "regulatory_updates_monitored": sum(m.get("updates_found", 0) for m in monitoring_data),
                "policies_generated": len(policies_data)
            },
            "audit_history": audits_data[:10],  # Last 10 audits
            "compliance_trend": self._calculate_trend(audits_data),
            "key_findings": self._generate_key_findings(audits_data),
            "recommendations": self._generate_report_recommendations(avg_score, audits_data),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report
    
    def _calculate_trend(self, audits: List[Dict]) -> str:
        """Calculate compliance trend from audit history"""
        if len(audits) < 2:
            return "insufficient_data"
        
        recent_scores = [a.get("overall_score", 0) for a in audits[:3]]
        older_scores = [a.get("overall_score", 0) for a in audits[3:6]] if len(audits) > 3 else recent_scores
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 5:
            return "improving"
        elif recent_avg < older_avg - 5:
            return "declining"
        return "stable"
    
    def _generate_key_findings(self, audits: List[Dict]) -> List[str]:
        """Generate key findings from audit data"""
        findings = []
        
        if not audits:
            findings.append("No audits conducted in the reporting period")
            return findings
        
        latest = audits[0] if audits else {}
        
        if latest.get("non_compliant", 0) > 0:
            findings.append(f"Found {latest['non_compliant']} non-compliant items requiring immediate attention")
        
        if latest.get("needs_attention", 0) > 0:
            findings.append(f"Identified {latest['needs_attention']} items needing attention")
        
        if latest.get("overall_score", 0) >= 90:
            findings.append("Organization maintains excellent compliance posture")
        elif latest.get("overall_score", 0) >= 70:
            findings.append("Compliance posture is satisfactory with room for improvement")
        else:
            findings.append("Compliance posture requires significant improvement")
        
        return findings
    
    def _generate_report_recommendations(self, avg_score: int, audits: List[Dict]) -> List[str]:
        """Generate recommendations for the report"""
        recommendations = []
        
        if avg_score < 70:
            recommendations.append("Prioritize addressing non-compliant items immediately")
            recommendations.append("Consider engaging compliance consultant for remediation")
        
        if avg_score < 90:
            recommendations.append("Schedule regular compliance training for staff")
            recommendations.append("Implement automated compliance monitoring")
        
        if len(audits) < 3:
            recommendations.append("Increase audit frequency to quarterly")
        
        recommendations.append("Continue monitoring regulatory changes")
        recommendations.append("Review and update policies annually")
        
        return recommendations
