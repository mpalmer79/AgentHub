from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from app.api.integrations import get_quickbooks_client
from app.core.database import get_supabase


class QuickBooksTools:
    """Tools for interacting with QuickBooks API"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._client_info = None
    
    async def _get_client(self) -> Dict[str, str]:
        """Get authenticated QuickBooks client info"""
        if not self._client_info:
            self._client_info = await get_quickbooks_client(self.user_id)
        return self._client_info
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to QuickBooks API"""
        client_info = await self._get_client()
        url = f"{client_info['base_url']}/v3/company/{client_info['realm_id']}/{endpoint}"
        
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
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"QuickBooks API error: {response.status_code}",
                "details": response.text
            }
    
    async def get_transactions(
        self,
        start_date: str,
        end_date: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch transactions from QuickBooks"""
        query = f"SELECT * FROM Purchase WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        
        if account_id:
            query += f" AND AccountRef = '{account_id}'"
        
        query += " ORDERBY TxnDate DESC MAXRESULTS 100"
        
        result = await self._make_request(
            "GET",
            "query",
            params={"query": query}
        )
        
        if "error" in result:
            return result
        
        purchases = result.get("QueryResponse", {}).get("Purchase", [])
        
        transactions = []
        for purchase in purchases:
            transactions.append({
                "id": purchase.get("Id"),
                "date": purchase.get("TxnDate"),
                "amount": purchase.get("TotalAmt"),
                "vendor": purchase.get("EntityRef", {}).get("name", "Unknown"),
                "account": purchase.get("AccountRef", {}).get("name", "Uncategorized"),
                "memo": purchase.get("PrivateNote", ""),
                "payment_type": purchase.get("PaymentType", ""),
                "line_items": [
                    {
                        "description": line.get("Description", ""),
                        "amount": line.get("Amount"),
                        "account": line.get("AccountBasedExpenseLineDetail", {}).get("AccountRef", {}).get("name", "")
                    }
                    for line in purchase.get("Line", [])
                    if line.get("DetailType") == "AccountBasedExpenseLineDetail"
                ]
            })
        
        return {
            "transactions": transactions,
            "count": len(transactions),
            "date_range": {"start": start_date, "end": end_date}
        }
    
    async def categorize_transaction(
        self,
        transaction_id: str,
        category: str,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Categorize a transaction"""
        accounts = await self.get_accounts(account_type="Expense")
        
        if "error" in accounts:
            return accounts
        
        target_account = None
        for account in accounts.get("accounts", []):
            if account["name"].lower() == category.lower():
                target_account = account
                break
        
        if not target_account:
            return {
                "error": f"Category '{category}' not found",
                "available_categories": [a["name"] for a in accounts.get("accounts", [])]
            }
        
        supabase = get_supabase()
        supabase.table("pending_categorizations").insert({
            "user_id": self.user_id,
            "transaction_id": transaction_id,
            "new_category": category,
            "account_id": target_account["id"],
            "memo": memo,
            "status": "pending_approval",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "pending_approval",
            "message": f"Transaction {transaction_id} queued for categorization to '{category}'",
            "requires_approval": True
        }
    
    async def get_accounts(
        self,
        account_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get list of accounts"""
        query = "SELECT * FROM Account WHERE Active = true"
        
        if account_type:
            query += f" AND AccountType = '{account_type}'"
        
        query += " ORDERBY Name"
        
        result = await self._make_request(
            "GET",
            "query",
            params={"query": query}
        )
        
        if "error" in result:
            return result
        
        accounts_data = result.get("QueryResponse", {}).get("Account", [])
        
        accounts = [
            {
                "id": account.get("Id"),
                "name": account.get("Name"),
                "type": account.get("AccountType"),
                "sub_type": account.get("AccountSubType"),
                "balance": account.get("CurrentBalance", 0),
                "fully_qualified_name": account.get("FullyQualifiedName")
            }
            for account in accounts_data
        ]
        
        return {"accounts": accounts, "count": len(accounts)}
    
    async def get_account_balance(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """Get balance for a specific account"""
        result = await self._make_request(
            "GET",
            f"account/{account_id}"
        )
        
        if "error" in result:
            return result
        
        account = result.get("Account", {})
        
        return {
            "account_id": account_id,
            "name": account.get("Name"),
            "balance": account.get("CurrentBalance", 0),
            "type": account.get("AccountType"),
            "as_of": datetime.utcnow().isoformat()
        }
    
    async def create_expense_report(
        self,
        start_date: str,
        end_date: str,
        group_by: str = "category"
    ) -> Dict[str, Any]:
        """Generate an expense report"""
        transactions_result = await self.get_transactions(start_date, end_date)
        
        if "error" in transactions_result:
            return transactions_result
        
        transactions = transactions_result.get("transactions", [])
        
        report = {
            "date_range": {"start": start_date, "end": end_date},
            "total_expenses": 0,
            "transaction_count": len(transactions),
            "grouped_data": {},
            "generated_at": datetime.utcnow().isoformat()
        }
        
        for txn in transactions:
            amount = float(txn.get("amount", 0))
            report["total_expenses"] += amount
            
            if group_by == "category":
                key = txn.get("account", "Uncategorized")
            elif group_by == "vendor":
                key = txn.get("vendor", "Unknown")
            elif group_by == "month":
                date = txn.get("date", "")
                key = date[:7] if date else "Unknown"
            else:
                key = "All"
            
            if key not in report["grouped_data"]:
                report["grouped_data"][key] = {
                    "total": 0,
                    "count": 0,
                    "transactions": []
                }
            
            report["grouped_data"][key]["total"] += amount
            report["grouped_data"][key]["count"] += 1
            report["grouped_data"][key]["transactions"].append({
                "id": txn.get("id"),
                "date": txn.get("date"),
                "amount": amount,
                "vendor": txn.get("vendor"),
                "memo": txn.get("memo")
            })
        
        sorted_groups = sorted(
            report["grouped_data"].items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        report["grouped_data"] = dict(sorted_groups)
        
        return report
    
    async def flag_for_review(
        self,
        transaction_id: str,
        reason: str,
        suggested_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """Flag a transaction for human review"""
        supabase = get_supabase()
        
        flag_record = supabase.table("flagged_transactions").insert({
            "user_id": self.user_id,
            "transaction_id": transaction_id,
            "reason": reason,
            "suggested_action": suggested_action,
            "status": "pending_review",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "status": "flagged",
            "flag_id": flag_record.data[0]["id"] if flag_record.data else None,
            "message": f"Transaction {transaction_id} flagged for review",
            "reason": reason,
            "suggested_action": suggested_action
        }
