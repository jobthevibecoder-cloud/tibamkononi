from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.api.deps import get_current_user

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(request: RegisterRequest):
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {"email": request.email, "full_name": request.full_name, "role": request.role}
    }

@router.post("/login")
async def login(request: LoginRequest):
    return {
        "access_token": "mock_token",
        "token_type": "bearer",
        "user": {"email": request.email, "role": "PATIENT"}
    }

@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user
