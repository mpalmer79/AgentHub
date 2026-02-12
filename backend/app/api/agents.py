from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.core.database import get_supabase_user
from app.core.auth import get_current_user, CurrentUser
from app.agents.registry import AGENT_REGISTRY, AgentType

router = APIRouter()


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


class SubscribeRequest(BaseModel):
    agent_type: AgentType
    config: dict | None = None


class AgentRunRequest(BaseModel):
    agent_type: AgentType
    task: str
    context: dict | None = None


@router.get("/catalog")
async def get_agent_catalog():
    return {
        "agents": [
            {
                "type": agent_type.value,
                "name": info["name"],
                "description": info["description"],
                "price_monthly": info["price_monthly"],
                "features": info["features"],
                "integrations": info["integrations"],
                "category": info["category"],
                "status": info.get("status", "available"),
            }
            for agent_type, info in AGENT_REGISTRY.items()
        ]
    }


@router.get("/subscriptions")
async def get_my_subscriptions(user: CurrentUser = Depends(get_current_user)):
    supabase = get_supabase_user(user.token)
    result = (
        supabase.table("agent_subscriptions")
        .select("*")
        .eq("status", "active")
        .execute()
    )
    return {"subscriptions": result.data or []}


@router.post("/subscribe")
async def subscribe_to_agent(req: SubscribeRequest, user: CurrentUser = Depends(get_current_user)):
    if req.agent_type not in AGENT_REGISTRY:
        raise HTTPException(status_code=400, detail="Unknown agent type")

    supabase = get_supabase_user(user.token)

    # Idempotent subscription creation is better, but keep simple for now.
    inserted = supabase.table("agent_subscriptions").insert(
        {
            "agent_type": req.agent_type.value,
            "status": "active",
            "config": req.config or {},
            "created_at": utc_now_iso(),
        }
    )

    return {"subscription": inserted.data}


@router.post("/run")
async def run_agent(req: AgentRunRequest, user: CurrentUser = Depends(get_current_user)):
    # This endpoint should eventually enqueue jobs, not run inline.
    if req.agent_type not in AGENT_REGISTRY:
        raise HTTPException(status_code=400, detail="Unknown agent type")

    supabase = get_supabase_user(user.token)

    # Create a task record. Actual execution should be a job queue in Step 3.
    task = supabase.table("agent_tasks").insert(
        {
            "agent_type": req.agent_type.value,
            "task": req.task,
            "context": req.context or {},
            "status": "queued",
            "created_at": utc_now_iso(),
        }
    )

    return {"task": task.data}
