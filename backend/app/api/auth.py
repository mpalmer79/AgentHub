from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.core.database import get_supabase
from app.core.auth import get_current_user

router = APIRouter()


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
async def sign_up(request: SignUpRequest):
    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                    "company_name": request.company_name
                }
            }
        })
        
        if auth_response.user:
            supabase.table("users").insert({
                "id": auth_response.user.id,
                "email": request.email,
                "full_name": request.full_name,
                "company_name": request.company_name
            }).execute()
            
            return {
                "message": "Account created successfully",
                "user_id": auth_response.user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create account")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signin")
async def sign_in(request: SignInRequest):
    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.session:
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/signout")
async def sign_out(user = Depends(get_current_user)):
    return {"message": "Signed out successfully"}


@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("users").select("*").eq("id", user.id).single().execute()
    
    if result.data:
        return result.data
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.user_metadata.get("full_name"),
        "company_name": user.user_metadata.get("company_name")
    }
