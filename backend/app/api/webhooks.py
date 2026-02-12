from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
import stripe
import hmac
import hashlib
import base64
from app.core.config import settings
from app.core.database import get_supabase

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


def verify_quickbooks_signature(payload: bytes, signature: str, verifier_token: str) -> bool:
    """
    Verify QuickBooks webhook signature using HMAC-SHA256.
    
    QuickBooks sends the signature in the 'intuit-signature' header.
    The signature is a base64-encoded HMAC-SHA256 hash of the payload
    using the webhook verifier token as the key.
    """
    if not verifier_token:
        return False
    
    expected = base64.b64encode(
        hmac.new(
            verifier_token.encode('utf-8'),
            payload,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    return hmac.compare_digest(expected, signature)


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """Handle Stripe webhook events"""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    supabase = get_supabase()
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        
        if user_id:
            supabase.table("users") \
                .update({
                    "stripe_customer_id": session.get("customer"),
                    "subscription_status": "active"
                }) \
                .eq("id", user_id) \
                .execute()
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        
        user = supabase.table("users") \
            .select("id") \
            .eq("stripe_customer_id", customer_id) \
            .single() \
            .execute()
        
        if user.data:
            supabase.table("users") \
                .update({"subscription_status": subscription.get("status")}) \
                .eq("id", user.data["id"]) \
                .execute()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        
        user = supabase.table("users") \
            .select("id") \
            .eq("stripe_customer_id", customer_id) \
            .single() \
            .execute()
        
        if user.data:
            supabase.table("users") \
                .update({"subscription_status": "cancelled"}) \
                .eq("id", user.data["id"]) \
                .execute()
            
            supabase.table("agent_subscriptions") \
                .update({"status": "cancelled"}) \
                .eq("user_id", user.data["id"]) \
                .eq("status", "active") \
                .execute()
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        
        user = supabase.table("users") \
            .select("id, email") \
            .eq("stripe_customer_id", customer_id) \
            .single() \
            .execute()
        
        if user.data:
            supabase.table("users") \
                .update({"subscription_status": "past_due"}) \
                .eq("id", user.data["id"]) \
                .execute()
    
    return {"status": "success"}


@router.post("/quickbooks")
async def quickbooks_webhook(
    request: Request,
    intuit_signature: Optional[str] = Header(None, alias="intuit-signature")
):
    """
    Handle QuickBooks webhook events.
    
    SECURITY: Validates the intuit-signature header using HMAC-SHA256
    to ensure the webhook is genuinely from QuickBooks.
    """
    # FIXED: Verify signature before processing
    if not intuit_signature:
        raise HTTPException(status_code=401, detail="Missing QuickBooks signature")
    
    payload = await request.body()
    
    # Verify the signature
    if not verify_quickbooks_signature(
        payload, 
        intuit_signature, 
        settings.QUICKBOOKS_WEBHOOK_VERIFIER_TOKEN
    ):
        raise HTTPException(status_code=401, detail="Invalid QuickBooks signature")
    
    # Parse the verified payload
    import json
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event_notifications = data.get("eventNotifications", [])
    
    for notification in event_notifications:
        realm_id = notification.get("realmId")
        data_change_event = notification.get("dataChangeEvent", {})
        entities = data_change_event.get("entities", [])
        
        supabase = get_supabase()
        
        integration = supabase.table("user_integrations") \
            .select("user_id") \
            .eq("realm_id", realm_id) \
            .eq("integration_type", "quickbooks") \
            .eq("status", "active") \
            .single() \
            .execute()
        
        if integration.data:
            for entity in entities:
                supabase.table("webhook_events").insert({
                    "user_id": integration.data["user_id"],
                    "integration_type": "quickbooks",
                    "event_type": entity.get("operation"),
                    "entity_type": entity.get("name"),
                    "entity_id": entity.get("id"),
                    "payload": entity,
                    "processed": False
                }).execute()
    
    return {"status": "success"}
