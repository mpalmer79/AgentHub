from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_supabase_user
from app.core.auth import get_current_user, CurrentUser

router = APIRouter()


class TaskApproval(BaseModel):
    approved: bool
    feedback: Optional[str] = None


class TaskAction(BaseModel):
    action: str
    parameters: dict = {}


@router.get("/pending")
async def get_pending_tasks(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_user(user.token)
    result = (
        supabase.table("agent_tasks")
        .select("*")
        .eq("status", "awaiting_approval")
        .order("created_at", desc=True)
        .execute()
    )
    return {"pending_tasks": result.data or []}


@router.post("/{task_id}/approve")
async def approve_task(task_id: str, approval: TaskApproval, user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_user(user.token)

    task = (
        supabase.table("agent_tasks")
        .select("*")
        .eq("id", task_id)
        .single()
        .execute()
    )

    if not task.data:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.data.get("status") != "awaiting_approval":
        raise HTTPException(status_code=400, detail="Task is not awaiting approval")

    new_status = "approved" if approval.approved else "rejected"
    now = datetime.utcnow().isoformat()

    supabase.table("agent_tasks").update(
        {
            "status": new_status,
            "approval_feedback": approval.feedback,
            "approved_at": now if approval.approved else None,
            "rejected_at": now if not approval.approved else None,
        }
    ).eq("id", task_id).execute()

    if approval.approved:
        # Only the owner can queue tasks under RLS
        supabase.table("agent_task_queue").insert(
            {"task_id": task_id, "status": "queued", "created_at": now}
        )

    return {"status": new_status}
