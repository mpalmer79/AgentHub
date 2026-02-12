from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import httpx

from app.core.database import get_supabase
from app.agents.tools.quickbooks import QuickBooksTools


class CashFlowTools:
    """Tools for cash flow analysis and management"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.quickbooks = QuickBooksTools(user_id)
    
    async def project_cashflow(
        self,
        days_ahead: int = 90,
        include_recurring: bool = True
    ) -> Dict[str, Any]:
        """Project cash flow for the next N days"""
        supabase = get_supabase()
        
        # Get current cash position from QuickBooks
        accounts_result = await self.quickbooks.get_accounts(account_type="Bank")
        
        if "error" in accounts_result:
            return accounts_result
        
        bank_accounts = accounts_result.get("accounts", [])
        current_cash = sum(float(acc.get("balance", 0)) for acc in bank_accounts)
        
        # Get recent transactions to establish patterns
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        txns_result = await self.quickbooks.get_transactions(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        if "error" in txns_result:
            return txns_result
        
        transactions = txns_result.get("transactions", [])
        
        # Analyze patterns
        weekly_inflows = []
        weekly_outflows = []
        
        for txn in transactions:
            amount = float(txn.get("amount", 0))
            if amount > 0:
                weekly_outflows.append(amount)
            else:
                weekly_inflows.append(abs(amount))
        
        avg_weekly_inflow = sum(weekly_inflows) / 13 if weekly_inflows else 0
        avg_weekly_outflow = sum(weekly_outflows) / 13 if weekly_outflows else 0
        
        # Project future cash positions
        projections = []
        running_balance = current_cash
        
        for week in range(days_ahead // 7 + 1):
            week_date = datetime.utcnow() + timedelta(weeks=week)
            projected_inflow = avg_weekly_inflow
            projected_outflow = avg_weekly_outflow
            running_balance = running_balance + projected_inflow - projected_outflow
            
            projections.append({
                "week": week + 1,
                "date": week_date.strftime("%Y-%m-%d"),
                "projected_inflow": round(projected_inflow, 2),
                "projected_outflow": round(projected_outflow, 2),
                "projected_balance": round(running_balance, 2),
                "net_change": round(projected_inflow - projected_outflow, 2)
            })
        
        # Identify potential cash crunches
        cash_crunches = []
        min_balance = current_cash * 0.1  # Alert if below 10% of current
        
        for proj in projections:
            if proj["projected_balance"] < min_balance:
                cash_crunches.append({
                    "week": proj["week"],
                    "date": proj["date"],
                    "projected_balance": proj["projected_balance"],
                    "shortfall": round(min_balance - proj["projected_balance"], 2)
                })
        
        # Store projection
        supabase.table("cashflow_projections").insert({
            "user_id": self.user_id,
            "projection_days": days_ahead,
            "current_cash": current_cash,
            "projections": projections,
            "cash_crunches": cash_crunches,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "current_cash_position": round(current_cash, 2),
            "projection_period_days": days_ahead,
            "summary": {
                "avg_weekly_inflow": round(avg_weekly_inflow, 2),
                "avg_weekly_outflow": round(avg_weekly_outflow, 2),
                "avg_weekly_net": round(avg_weekly_inflow - avg_weekly_outflow, 2),
                "ending_projected_balance": projections[-1]["projected_balance"] if projections else current_cash
            },
            "weekly_projections": projections,
            "cash_crunch_alerts": cash_crunches,
            "has_alerts": len(cash_crunches) > 0,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def prioritize_collections(
        self,
        min_amount: float = 100,
        days_overdue_threshold: int = 30
    ) -> Dict[str, Any]:
        """Analyze and prioritize accounts receivable for collection"""
        # Get accounts receivable
        ar_result = await self.quickbooks.get_accounts(account_type="Accounts Receivable")
        
        if "error" in ar_result:
            return ar_result
        
        # Get invoices/receivables
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)
        
        # Query for open invoices
        client_info = await self.quickbooks._get_client()
        query = f"SELECT * FROM Invoice WHERE Balance > 0 ORDER BY DueDate"
        
        result = await self.quickbooks._make_request(
            "GET",
            "query",
            params={"query": query}
        )
        
        receivables = []
        total_ar = 0
        
        if "error" not in result:
            invoices = result.get("QueryResponse", {}).get("Invoice", [])
            
            for inv in invoices:
                balance = float(inv.get("Balance", 0))
                if balance < min_amount:
                    continue
                
                due_date_str = inv.get("DueDate", "")
                days_overdue = 0
                
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                        days_overdue = (datetime.utcnow() - due_date).days
                    except ValueError:
                        pass
                
                customer_name = inv.get("CustomerRef", {}).get("name", "Unknown")
                
                # Calculate priority score
                priority_score = 0
                if days_overdue > 90:
                    priority_score = 100
                elif days_overdue > 60:
                    priority_score = 80
                elif days_overdue > 30:
                    priority_score = 60
                elif days_overdue > 0:
                    priority_score = 40
                else:
                    priority_score = 20
                
                # Adjust for amount
                if balance > 10000:
                    priority_score = priority_score + 20
                elif balance > 5000:
                    priority_score = priority_score + 10
                
                receivables.append({
                    "invoice_id": inv.get("Id"),
                    "invoice_number": inv.get("DocNumber"),
                    "customer": customer_name,
                    "amount": balance,
                    "due_date": due_date_str,
                    "days_overdue": max(0, days_overdue),
                    "priority_score": min(100, priority_score),
                    "aging_bucket": self._get_aging_bucket(days_overdue),
                    "recommended_action": self._get_collection_action(days_overdue, balance)
                })
                
                total_ar = total_ar + balance
        
        # Sort by priority
        receivables.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Aging summary
        aging_summary = {
            "current": sum(r["amount"] for r in receivables if r["days_overdue"] <= 0),
            "1_30_days": sum(r["amount"] for r in receivables if 0 < r["days_overdue"] <= 30),
            "31_60_days": sum(r["amount"] for r in receivables if 30 < r["days_overdue"] <= 60),
            "61_90_days": sum(r["amount"] for r in receivables if 60 < r["days_overdue"] <= 90),
            "over_90_days": sum(r["amount"] for r in receivables if r["days_overdue"] > 90)
        }
        
        return {
            "total_receivables": round(total_ar, 2),
            "receivables_count": len(receivables),
            "aging_summary": {k: round(v, 2) for k, v in aging_summary.items()},
            "priority_collections": receivables[:20],
            "high_priority_count": len([r for r in receivables if r["priority_score"] >= 60]),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_aging_bucket(self, days_overdue: int) -> str:
        if days_overdue <= 0:
            return "Current"
        elif days_overdue <= 30:
            return "1-30 Days"
        elif days_overdue <= 60:
            return "31-60 Days"
        elif days_overdue <= 90:
            return "61-90 Days"
        else:
            return "Over 90 Days"
    
    def _get_collection_action(self, days_overdue: int, amount: float) -> str:
        if days_overdue > 90:
            return "Final notice - consider collection agency"
        elif days_overdue > 60:
            return "Send formal demand letter"
        elif days_overdue > 30:
            return "Phone call follow-up required"
        elif days_overdue > 0:
            return "Send payment reminder email"
        else:
            return "No action needed yet"
    
    async def optimize_payments(
        self,
        available_cash: Optional[float] = None
    ) -> Dict[str, Any]:
        """Optimize payment timing to maximize cash position"""
        # Get accounts payable
        ap_result = await self.quickbooks.get_accounts(account_type="Accounts Payable")
        
        if "error" in ap_result and "error" in str(ap_result):
            return ap_result
        
        # Query for bills
        query = "SELECT * FROM Bill WHERE Balance > 0 ORDER BY DueDate"
        
        result = await self.quickbooks._make_request(
            "GET",
            "query",
            params={"query": query}
        )
        
        payables = []
        total_ap = 0
        
        if "error" not in result:
            bills = result.get("QueryResponse", {}).get("Bill", [])
            
            for bill in bills:
                balance = float(bill.get("Balance", 0))
                due_date_str = bill.get("DueDate", "")
                
                days_until_due = 0
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                        days_until_due = (due_date - datetime.utcnow()).days
                    except ValueError:
                        pass
                
                vendor_name = bill.get("VendorRef", {}).get("name", "Unknown")
                
                # Determine payment strategy
                if days_until_due < 0:
                    urgency = "overdue"
                    strategy = "Pay immediately to avoid penalties"
                elif days_until_due <= 7:
                    urgency = "due_soon"
                    strategy = "Schedule payment this week"
                elif days_until_due <= 14:
                    urgency = "upcoming"
                    strategy = "Schedule payment next week"
                else:
                    urgency = "not_urgent"
                    strategy = "Hold until closer to due date"
                
                payables.append({
                    "bill_id": bill.get("Id"),
                    "vendor": vendor_name,
                    "amount": balance,
                    "due_date": due_date_str,
                    "days_until_due": days_until_due,
                    "urgency": urgency,
                    "payment_strategy": strategy
                })
                
                total_ap = total_ap + balance
        
        # Sort by urgency
        urgency_order = {"overdue": 0, "due_soon": 1, "upcoming": 2, "not_urgent": 3}
        payables.sort(key=lambda x: (urgency_order.get(x["urgency"], 4), x["days_until_due"]))
        
        # Calculate optimal payment schedule
        if available_cash is None:
            accounts = await self.quickbooks.get_accounts(account_type="Bank")
            if "error" not in accounts:
                available_cash = sum(float(a.get("balance", 0)) for a in accounts.get("accounts", []))
            else:
                available_cash = 0
        
        pay_now = []
        defer = []
        running_total = 0
        
        for payable in payables:
            if payable["urgency"] in ["overdue", "due_soon"]:
                pay_now.append(payable)
                running_total = running_total + payable["amount"]
            elif running_total + payable["amount"] <= available_cash * 0.7:
                pay_now.append(payable)
                running_total = running_total + payable["amount"]
            else:
                defer.append(payable)
        
        return {
            "available_cash": round(available_cash, 2),
            "total_payables": round(total_ap, 2),
            "recommendation": {
                "pay_now_total": round(sum(p["amount"] for p in pay_now), 2),
                "defer_total": round(sum(p["amount"] for p in defer), 2),
                "projected_remaining_cash": round(available_cash - running_total, 2)
            },
            "pay_now": pay_now,
            "defer_payment": defer,
            "overdue_count": len([p for p in payables if p["urgency"] == "overdue"]),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def send_invoice_reminder(
        self,
        customer_name: str,
        invoice_number: str,
        amount: float,
        days_overdue: int,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate and track invoice payment reminder"""
        supabase = get_supabase()
        
        # Determine reminder type based on days overdue
        if days_overdue > 60:
            reminder_type = "final_notice"
            subject = f"FINAL NOTICE: Invoice #{invoice_number} - Payment Required"
            urgency = "This is our final reminder before further action."
        elif days_overdue > 30:
            reminder_type = "second_reminder"
            subject = f"Second Reminder: Invoice #{invoice_number} Past Due"
            urgency = "Please prioritize this payment to avoid any service interruptions."
        else:
            reminder_type = "first_reminder"
            subject = f"Friendly Reminder: Invoice #{invoice_number}"
            urgency = "We would appreciate your prompt attention to this matter."
        
        body = f"""Dear {customer_name},

This is a reminder regarding Invoice #{invoice_number} for ${amount:,.2f}, which is {days_overdue} days past due.

{urgency}

If you have already sent payment, please disregard this notice and accept our thanks.

If you have any questions about this invoice or need to discuss payment arrangements, please don't hesitate to contact us.

Best regards,
Accounts Receivable"""
        
        # Store the reminder
        reminder = supabase.table("invoice_reminders").insert({
            "user_id": self.user_id,
            "customer_name": customer_name,
            "invoice_number": invoice_number,
            "amount": amount,
            "days_overdue": days_overdue,
            "reminder_type": reminder_type,
            "customer_email": customer_email,
            "status": "generated",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "reminder_id": reminder.data[0]["id"] if reminder.data else None,
            "reminder_type": reminder_type,
            "customer": customer_name,
            "invoice_number": invoice_number,
            "amount": amount,
            "days_overdue": days_overdue,
            "email_draft": {
                "to": customer_email,
                "subject": subject,
                "body": body
            },
            "status": "ready_to_send",
            "message": f"Payment reminder generated for Invoice #{invoice_number}"
        }
    
    async def score_customer_risk(
        self,
        customer_name: str
    ) -> Dict[str, Any]:
        """Assess payment risk score for a customer"""
        # Query customer payment history
        query = f"SELECT * FROM Invoice WHERE CustomerRef.name = '{customer_name}'"
        
        result = await self.quickbooks._make_request(
            "GET",
            "query",
            params={"query": query}
        )
        
        if "error" in result:
            return result
        
        invoices = result.get("QueryResponse", {}).get("Invoice", [])
        
        if not invoices:
            return {
                "customer": customer_name,
                "risk_score": 50,
                "risk_level": "unknown",
                "message": "No payment history available for this customer",
                "recommendation": "Request payment upfront or partial deposit"
            }
        
        total_invoices = len(invoices)
        paid_invoices = [inv for inv in invoices if float(inv.get("Balance", 0)) == 0]
        open_invoices = [inv for inv in invoices if float(inv.get("Balance", 0)) > 0]
        
        total_billed = sum(float(inv.get("TotalAmt", 0)) for inv in invoices)
        total_outstanding = sum(float(inv.get("Balance", 0)) for inv in open_invoices)
        
        # Calculate average days to payment for paid invoices
        payment_days = []
        for inv in paid_invoices:
            created = inv.get("TxnDate", "")
            due = inv.get("DueDate", "")
            if created and due:
                try:
                    created_date = datetime.strptime(created, "%Y-%m-%d")
                    due_date = datetime.strptime(due, "%Y-%m-%d")
                    payment_days.append((due_date - created_date).days)
                except ValueError:
                    pass
        
        avg_payment_days = sum(payment_days) / len(payment_days) if payment_days else 30
        
        # Calculate risk score (0-100, lower is better)
        risk_score = 50  # Base score
        
        # Adjust based on payment history
        if total_invoices > 5:
            payment_rate = len(paid_invoices) / total_invoices
            if payment_rate > 0.9:
                risk_score = risk_score - 20
            elif payment_rate > 0.7:
                risk_score = risk_score - 10
            elif payment_rate < 0.5:
                risk_score = risk_score + 20
        
        # Adjust based on outstanding balance
        if total_outstanding > 10000:
            risk_score = risk_score + 15
        elif total_outstanding > 5000:
            risk_score = risk_score + 10
        
        # Adjust based on payment timing
        if avg_payment_days > 45:
            risk_score = risk_score + 15
        elif avg_payment_days < 15:
            risk_score = risk_score - 10
        
        risk_score = max(0, min(100, risk_score))
        
        # Determine risk level
        if risk_score <= 30:
            risk_level = "low"
            recommendation = "Standard payment terms acceptable"
        elif risk_score <= 50:
            risk_level = "moderate"
            recommendation = "Consider shorter payment terms"
        elif risk_score <= 70:
            risk_level = "elevated"
            recommendation = "Request deposit or partial payment upfront"
        else:
            risk_level = "high"
            recommendation = "Require prepayment or COD terms"
        
        return {
            "customer": customer_name,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "payment_history": {
                "total_invoices": total_invoices,
                "paid_invoices": len(paid_invoices),
                "open_invoices": len(open_invoices),
                "total_billed": round(total_billed, 2),
                "total_outstanding": round(total_outstanding, 2),
                "avg_payment_days": round(avg_payment_days, 1)
            },
            "recommendation": recommendation,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def get_cash_alerts(self) -> Dict[str, Any]:
        """Get current cash flow alerts and warnings"""
        alerts = []
        
        # Check current cash position
        accounts = await self.quickbooks.get_accounts(account_type="Bank")
        if "error" not in accounts:
            current_cash = sum(float(a.get("balance", 0)) for a in accounts.get("accounts", []))
            
            if current_cash < 5000:
                alerts.append({
                    "type": "critical",
                    "category": "low_cash",
                    "message": f"Critical: Cash balance is ${current_cash:,.2f}",
                    "action": "Prioritize collections and defer non-essential payments"
                })
            elif current_cash < 10000:
                alerts.append({
                    "type": "warning",
                    "category": "low_cash",
                    "message": f"Warning: Cash balance is ${current_cash:,.2f}",
                    "action": "Monitor cash position closely"
                })
        
        # Check overdue receivables
        collections = await self.prioritize_collections(min_amount=500, days_overdue_threshold=30)
        if "error" not in collections:
            overdue_90 = collections.get("aging_summary", {}).get("over_90_days", 0)
            if overdue_90 > 5000:
                alerts.append({
                    "type": "warning",
                    "category": "overdue_receivables",
                    "message": f"${overdue_90:,.2f} in receivables over 90 days",
                    "action": "Escalate collection efforts"
                })
        
        # Check overdue payables
        payments = await self.optimize_payments()
        if "error" not in payments:
            overdue_count = payments.get("overdue_count", 0)
            if overdue_count > 0:
                alerts.append({
                    "type": "warning",
                    "category": "overdue_payables",
                    "message": f"{overdue_count} bills are past due",
                    "action": "Review and pay overdue bills to avoid penalties"
                })
        
        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "critical_count": len([a for a in alerts if a["type"] == "critical"]),
            "warning_count": len([a for a in alerts if a["type"] == "warning"]),
            "checked_at": datetime.utcnow().isoformat()
        }
