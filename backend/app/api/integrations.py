from typing import Dict
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import httpx
import secrets
from urllib.parse import urlencode

from app.core.config import settings
from app.core.database import get_supabase, get_supabase_user
from app.core.auth import get_current_user, CurrentUser
from app.core.crypto import encryption_service  # NEW: Import encryption

router = APIRouter()


class IntegrationStatus(BaseModel):
    integration_type: str
    connected: bool
    connected_at: Optional[str] = None
    account_name: Optional[str] = None


# QuickBooks OAuth URLs
QUICKBOOKS_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
QUICKBOOKS_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
QUICKBOOKS_API_BASE = "https://sandbox-quickbooks.api.intuit.com" if settings.QUICKBOOKS_ENVIRONMENT == "sandbox" else "https://quickbooks.api.intuit.com"

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Gmail API Scopes
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# Google Calendar Scopes
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


@router.get("/status")
async def get_integration_status(user: CurrentUser = Depends(get_current_user)):
    """Get status of all integrations for the user"""
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    result = supabase.table("user_integrations") \
        .select("*") \
        .execute()  # RLS filters by user_id automatically
    
    integrations = {item["integration_type"]: item for item in (result.data or [])}
    
    return {
        "integrations": [
            {
                "type": "quickbooks",
                "name": "QuickBooks Online",
                "description": "Accounting and bookkeeping",
                "connected": "quickbooks" in integrations and integrations["quickbooks"].get("status") == "active",
                "connected_at": integrations.get("quickbooks", {}).get("connected_at"),
                "account_name": integrations.get("quickbooks", {}).get("account_name")
            },
            {
                "type": "gmail",
                "name": "Gmail",
                "description": "Email management",
                "connected": "gmail" in integrations and integrations["gmail"].get("status") == "active",
                "connected_at": integrations.get("gmail", {}).get("connected_at"),
                "account_name": integrations.get("gmail", {}).get("account_name")
            },
            {
                "type": "google_calendar",
                "name": "Google Calendar",
                "description": "Calendar and scheduling",
                "connected": "google_calendar" in integrations and integrations["google_calendar"].get("status") == "active",
                "connected_at": integrations.get("google_calendar", {}).get("connected_at"),
                "account_name": integrations.get("google_calendar", {}).get("account_name")
            }
        ]
    }


# =============================================================================
# QUICKBOOKS OAUTH
# =============================================================================

@router.get("/quickbooks/connect")
async def quickbooks_connect(user: CurrentUser = Depends(get_current_user)):
    """Initiate QuickBooks OAuth flow"""
    state = secrets.token_urlsafe(32)
    
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    supabase.table("oauth_states").insert({
        "state": state,
        "user_id": user.id,
        "integration_type": "quickbooks",
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    scopes = "com.intuit.quickbooks.accounting"
    auth_url = (
        f"{QUICKBOOKS_AUTH_URL}?"
        f"client_id={settings.QUICKBOOKS_CLIENT_ID}"
        f"&response_type=code"
        f"&scope={scopes}"
        f"&redirect_uri={settings.QUICKBOOKS_REDIRECT_URI}"
        f"&state={state}"
    )
    
    return {"auth_url": auth_url}


@router.get("/quickbooks/callback")
async def quickbooks_callback(code: str, state: str, realmId: str):
    """Handle QuickBooks OAuth callback"""
    supabase = get_supabase()  # Admin needed for callback (no user session yet)
    
    state_record = supabase.table("oauth_states") \
        .select("*") \
        .eq("state", state) \
        .single() \
        .execute()
    
    if not state_record.data:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    user_id = state_record.data["user_id"]
    
    supabase.table("oauth_states").delete().eq("state", state).execute()
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            QUICKBOOKS_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.QUICKBOOKS_REDIRECT_URI
            },
            auth=(settings.QUICKBOOKS_CLIENT_ID, settings.QUICKBOOKS_CLIENT_SECRET),
            headers={"Accept": "application/json"}
        )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
    
    tokens = token_response.json()
    
    async with httpx.AsyncClient() as client:
        company_response = await client.get(
            f"{QUICKBOOKS_API_BASE}/v3/company/{realmId}/companyinfo/{realmId}",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "Accept": "application/json"
            }
        )
    
    company_name = None
    if company_response.status_code == 200:
        company_data = company_response.json()
        company_name = company_data.get("CompanyInfo", {}).get("CompanyName")
    
    existing = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "quickbooks") \
        .execute()
    
    # FIXED: Encrypt tokens before storage
    integration_data = {
        "user_id": user_id,
        "integration_type": "quickbooks",
        "status": "active",
        "access_token": encryption_service.encrypt(tokens["access_token"]),
        "refresh_token": encryption_service.encrypt(tokens["refresh_token"]),
        "token_expires_at": datetime.utcnow().timestamp() + tokens.get("expires_in", 3600),
        "realm_id": realmId,
        "account_name": company_name,
        "connected_at": datetime.utcnow().isoformat()
    }
    
    if existing.data:
        supabase.table("user_integrations") \
            .update(integration_data) \
            .eq("user_id", user_id) \
            .eq("integration_type", "quickbooks") \
            .execute()
    else:
        supabase.table("user_integrations").insert(integration_data).execute()
    
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard/integrations?connected=quickbooks")


@router.delete("/quickbooks/disconnect")
async def quickbooks_disconnect(user: CurrentUser = Depends(get_current_user)):
    """Disconnect QuickBooks integration"""
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    
    supabase.table("user_integrations") \
        .update({"status": "disconnected", "disconnected_at": datetime.utcnow().isoformat()}) \
        .eq("integration_type", "quickbooks") \
        .execute()  # RLS filters by user_id
    
    return {"message": "QuickBooks disconnected successfully"}


async def get_quickbooks_client(user_id: str):
    """Get an authenticated QuickBooks client for a user"""
    supabase = get_supabase()  # Admin needed to read other user's integrations for workers
    integration = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "quickbooks") \
        .eq("status", "active") \
        .single() \
        .execute()
    
    if not integration.data:
        raise HTTPException(status_code=400, detail="QuickBooks not connected")
    
    # FIXED: Decrypt tokens when reading
    access_token = encryption_service.decrypt(integration.data["access_token"])
    refresh_token = encryption_service.decrypt(integration.data["refresh_token"])
    
    if datetime.utcnow().timestamp() > integration.data["token_expires_at"]:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                QUICKBOOKS_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                auth=(settings.QUICKBOOKS_CLIENT_ID, settings.QUICKBOOKS_CLIENT_SECRET),
                headers={"Accept": "application/json"}
            )
        
        if token_response.status_code != 200:
            supabase.table("user_integrations") \
                .update({"status": "expired"}) \
                .eq("user_id", user_id) \
                .eq("integration_type", "quickbooks") \
                .execute()
            raise HTTPException(status_code=401, detail="QuickBooks token expired, please reconnect")
        
        tokens = token_response.json()
        
        # FIXED: Encrypt new tokens before storage
        supabase.table("user_integrations") \
            .update({
                "access_token": encryption_service.encrypt(tokens["access_token"]),
                "refresh_token": encryption_service.encrypt(tokens.get("refresh_token", refresh_token)),
                "token_expires_at": datetime.utcnow().timestamp() + tokens.get("expires_in", 3600)
            }) \
            .eq("user_id", user_id) \
            .eq("integration_type", "quickbooks") \
            .execute()
        
        access_token = tokens["access_token"]
    
    return {
        "access_token": access_token,
        "realm_id": integration.data["realm_id"],
        "base_url": QUICKBOOKS_API_BASE
    }


# =============================================================================
# GMAIL OAUTH
# =============================================================================

@router.get("/gmail/connect")
async def gmail_connect(user: CurrentUser = Depends(get_current_user)):
    """Initiate Gmail OAuth flow"""
    state = secrets.token_urlsafe(32)
    
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    supabase.table("oauth_states").insert({
        "state": state,
        "user_id": user.id,
        "integration_type": "gmail",
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GMAIL_SCOPES),
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    return {"auth_url": auth_url}


@router.get("/gmail/callback")
async def gmail_callback(code: str, state: str):
    """Handle Gmail OAuth callback"""
    supabase = get_supabase()  # Admin needed for callback
    
    state_record = supabase.table("oauth_states") \
        .select("*") \
        .eq("state", state) \
        .single() \
        .execute()
    
    if not state_record.data:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    user_id = state_record.data["user_id"]
    
    supabase.table("oauth_states").delete().eq("state", state).execute()
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
    
    tokens = token_response.json()
    
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
    
    account_email = None
    if userinfo_response.status_code == 200:
        userinfo = userinfo_response.json()
        account_email = userinfo.get("email")
    
    existing = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "gmail") \
        .execute()
    
    # FIXED: Encrypt tokens before storage
    integration_data = {
        "user_id": user_id,
        "integration_type": "gmail",
        "status": "active",
        "access_token": encryption_service.encrypt(tokens["access_token"]),
        "refresh_token": encryption_service.encrypt(tokens.get("refresh_token")),
        "token_expires_at": datetime.utcnow().timestamp() + tokens.get("expires_in", 3600),
        "account_name": account_email,
        "connected_at": datetime.utcnow().isoformat()
    }
    
    if existing.data:
        supabase.table("user_integrations") \
            .update(integration_data) \
            .eq("user_id", user_id) \
            .eq("integration_type", "gmail") \
            .execute()
    else:
        supabase.table("user_integrations").insert(integration_data).execute()
    
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard/integrations?connected=gmail")


@router.delete("/gmail/disconnect")
async def gmail_disconnect(user: CurrentUser = Depends(get_current_user)):
    """Disconnect Gmail integration"""
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    
    supabase.table("user_integrations") \
        .update({"status": "disconnected", "disconnected_at": datetime.utcnow().isoformat()}) \
        .eq("integration_type", "gmail") \
        .execute()
    
    return {"message": "Gmail disconnected successfully"}


async def get_gmail_client(user_id: str):
    """Get an authenticated Gmail client for a user"""
    supabase = get_supabase()  # Admin needed for workers
    integration = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "gmail") \
        .eq("status", "active") \
        .single() \
        .execute()
    
    if not integration.data:
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    # FIXED: Decrypt tokens when reading
    access_token = encryption_service.decrypt(integration.data["access_token"])
    refresh_token = encryption_service.decrypt(integration.data.get("refresh_token"))
    
    if datetime.utcnow().timestamp() > integration.data["token_expires_at"]:
        if not refresh_token:
            supabase.table("user_integrations") \
                .update({"status": "expired"}) \
                .eq("user_id", user_id) \
                .eq("integration_type", "gmail") \
                .execute()
            raise HTTPException(status_code=401, detail="Gmail token expired, please reconnect")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        if token_response.status_code != 200:
            supabase.table("user_integrations") \
                .update({"status": "expired"}) \
                .eq("user_id", user_id) \
                .eq("integration_type", "gmail") \
                .execute()
            raise HTTPException(status_code=401, detail="Gmail token expired, please reconnect")
        
        tokens = token_response.json()
        
        # FIXED: Encrypt new token before storage
        supabase.table("user_integrations") \
            .update({
                "access_token": encryption_service.encrypt(tokens["access_token"]),
                "token_expires_at": datetime.utcnow().timestamp() + tokens.get("expires_in", 3600)
            }) \
            .eq("user_id", user_id) \
            .eq("integration_type", "gmail") \
            .execute()
        
        access_token = tokens["access_token"]
    
    return {
        "access_token": access_token
    }


# =============================================================================
# GOOGLE CALENDAR OAUTH
# =============================================================================

@router.get("/google_calendar/connect")
async def google_calendar_connect(user: CurrentUser = Depends(get_current_user)):
    """Initiate Google Calendar OAuth flow"""
    state = secrets.token_urlsafe(32)
    
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    supabase.table("oauth_states").insert({
        "state": state,
        "user_id": user.id,
        "integration_type": "google_calendar",
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_CALENDAR_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(CALENDAR_SCOPES),
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    return {"auth_url": auth_url}


@router.get("/google_calendar/callback")
async def google_calendar_callback(code: str, state: str):
    """Handle Google Calendar OAuth callback"""
    supabase = get_supabase()  # Admin needed for callback
    
    state_record = supabase.table("oauth_states") \
        .select("*") \
        .eq("state", state) \
        .single() \
        .execute()
    
    if not state_record.data:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    user_id = state_record.data["user_id"]
    
    supabase.table("oauth_states").delete().eq("state", state).execute()
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_CALENDAR_REDIRECT_URI
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
    
    tokens = token_response.json()
    
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
    
    account_email = None
    if userinfo_response.status_code == 200:
        userinfo = userinfo_response.json()
        account_email = userinfo.get("email")
    
    existing = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "google_calendar") \
        .execute()
    
    # FIXED: Encrypt tokens before storage
    integration_data = {
        "user_id": user_id,
        "integration_type": "google_calendar",
        "status": "active",
        "access_token": encryption_service.encrypt(tokens["access_token"]),
        "refresh_token": encryption_service.encrypt(tokens.get("refresh_token")),
        "token_expires_at": datetime.utcnow().timestamp() + tokens.get("expires_in", 3600),
        "account_name": account_email,
        "connected_at": datetime.utcnow().isoformat()
    }
    
    if existing.data:
        supabase.table("user_integrations") \
            .update(integration_data) \
            .eq("user_id", user_id) \
            .eq("integration_type", "google_calendar") \
            .execute()
    else:
        supabase.table("user_integrations").insert(integration_data).execute()
    
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard/integrations?connected=google_calendar")


@router.delete("/google_calendar/disconnect")
async def google_calendar_disconnect(user: CurrentUser = Depends(get_current_user)):
    """Disconnect Google Calendar integration"""
    supabase = get_supabase_user(user.token)  # FIXED: Use user-scoped client
    
    supabase.table("user_integrations") \
        .update({"status": "disconnected", "disconnected_at": datetime.utcnow().isoformat()}) \
        .eq("integration_type", "google_calendar") \
        .execute()
    
    return {"message": "Google Calendar disconnected successfully"}


async def get_google_calendar_client(user_id: str):
    """Get an authenticated Google Calendar client for a user"""
    supabase = get_supabase()  # Admin needed for workers
    integration = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "google_calendar") \
        .eq("status", "active") \
        .single() \
        .execute()
    
    if not integration.data:
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    # FIXED: Decrypt tokens when reading
    access_token = encryption_service.decrypt(integration.data["access_token"])
    refresh_token = encryption_service.decrypt(integration.data.get("refresh_token"))
    
    if datetime.utcnow().timestamp() > integration.data["token_expires_at"]:
        if not refresh_token:
            supabase.table("user_integrations") \
                .update({"status": "expired"}) \
                .eq("user_id", user_id) \
                .eq("integration_type", "google_calendar") \
                .execute()
            raise HTTPException(status_code=401, detail="Google Calendar token expired, please reconnect")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        if token_response.status_code != 200:
            supabase.table("user_integrations") \
                .update({"status": "expired"}) \
                .eq("user_id", user_id) \
                .eq("integration_type", "google_calendar") \
                .execute()
            raise HTTPException(status_code=401, detail="Google Calendar token expired, please reconnect")
        
        tokens = token_response.json()
        
        # FIXED: Encrypt new token before storage
        supabase.table("user_integrations") \
            .update({
                "access_token": encryption_service.encrypt(tokens["access_token"]),
                "token_expires_at": datetime.utcnow().timestamp() + tokens.get("expires_in", 3600)
            }) \
            .eq("user_id", user_id) \
            .eq("integration_type", "google_calendar") \
            .execute()
        
        access_token = tokens["access_token"]
    
    return {
        "access_token": access_token
    }


# =============================================================================
# ZENDESK OAUTH (STUB - For CustomerCareAI)
# =============================================================================

async def get_zendesk_client(user_id: str) -> Dict[str, str]:
    """Get authenticated Zendesk client info for a user"""
    supabase = get_supabase()
    integration = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "zendesk") \
        .eq("status", "active") \
        .single() \
        .execute()
    
    if not integration.data:
        return {
            "access_token": "mock_zendesk_token",
            "subdomain": "mock-company"
        }
    
    return {
        "access_token": encryption_service.decrypt(integration.data.get("access_token", "")),
        "subdomain": integration.data.get("subdomain", "")
    }


# =============================================================================
# META (FACEBOOK/INSTAGRAM) OAUTH (STUB - For SocialPilotAI)
# =============================================================================

async def get_meta_client(user_id: str) -> Dict[str, str]:
    """Get authenticated Meta (Facebook/Instagram) client info for a user"""
    supabase = get_supabase()
    integration = supabase.table("user_integrations") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("integration_type", "meta") \
        .eq("status", "active") \
        .single() \
        .execute()
    
    if not integration.data:
        return {
            "access_token": "mock_meta_token",
            "page_id": "mock_page_123"
        }
    
    return {
        "access_token": encryption_service.decrypt(integration.data.get("access_token", "")),
        "page_id": integration.data.get("page_id", "")
    }
