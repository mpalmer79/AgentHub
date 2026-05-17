from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_supabase
from app.core.logging import get_logger
from app.core.ratelimit import limiter

router = APIRouter()
log = get_logger(__name__)


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str | None = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    company_name: str | None
    created_at: str


@router.post("/signup")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def sign_up(request: Request, payload: SignUpRequest):
    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {
                    "full_name": payload.full_name,
                    "company_name": payload.company_name,
                }
            },
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create account")

        supabase.table("users").insert({
            "id": auth_response.user.id,
            "email": payload.email,
            "full_name": payload.full_name,
            "company_name": payload.company_name,
        }).execute()

        return {
            "message": "Account created successfully",
            "user_id": auth_response.user.id,
        }

    except HTTPException:
        raise
    except Exception as exc:
        # Don't leak provider error messages to the client; log them server-side.
        log.warning("signup_failed", extra={"email": payload.email, "error": str(exc)})
        raise HTTPException(status_code=400, detail="Unable to create account")


@router.post("/signin")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def sign_in(request: Request, payload: SignInRequest):
    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })

        if not auth_response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        log.warning("signin_failed", extra={"email": payload.email, "error": str(exc)})
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/signout")
async def sign_out(user=Depends(get_current_user)):
    return {"message": "Signed out successfully"}


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    """Get current user profile. Uses user-scoped DB access."""
    supabase = get_supabase(user.token)
    result = supabase.table("users").select("*").eq("id", user.id).single().execute()

    if result.data:
        return result.data

    return {
        "id": user.id,
        "email": user.email,
        "full_name": None,
        "company_name": None,
    }
