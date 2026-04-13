"""Authentication endpoints: register, login, refresh, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user
)
from app.models.user import User

router = APIRouter()


# ── SCHEMAS ──
class StudentRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    student_id: str = Field(..., pattern=r"^[A-Z]{2,5}-\d{4}-\d{3,4}$")
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class RefreshRequest(BaseModel):
    refresh_token: str


# ── ENDPOINTS ──
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register_student(data: StudentRegisterRequest, db: Session = Depends(get_db)):
    """Register a new student account."""
    # Check duplicate email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    # Check duplicate student ID
    if db.query(User).filter(User.student_id == data.student_id).first():
        raise HTTPException(status_code=409, detail="Student ID already registered")

    user = User(
        name=data.name,
        email=data.email,
        student_id=data.student_id,
        hashed_password=hash_password(data.password),
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    tokens = _issue_tokens(user)
    return {**tokens, "user": _user_dict(user)}


@router.post("/login", response_model=TokenResponse)
async def login_student(data: LoginRequest, db: Session = Depends(get_db)):
    """Student login."""
    user = db.query(User).filter(User.email == data.email, User.role == "student").first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    user.last_login = datetime.utcnow()
    db.commit()
    tokens = _issue_tokens(user)
    return {**tokens, "user": _user_dict(user)}


@router.post("/admin/login", response_model=TokenResponse)
async def login_admin(data: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login."""
    user = db.query(User).filter(User.email == data.email, User.role == "admin").first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    user.last_login = datetime.utcnow()
    db.commit()
    tokens = _issue_tokens(user)
    return {**tokens, "user": _user_dict(user)}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user = db.query(User).filter(User.id == int(payload["sub"]), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    tokens = _issue_tokens(user)
    return {**tokens, "user": _user_dict(user)}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return _user_dict(current_user)


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)."""
    return {"message": "Logged out successfully"}


# ── HELPERS ──
def _issue_tokens(user: User) -> dict:
    payload = {"sub": str(user.id), "role": user.role, "email": user.email}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
    }


def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "student_id": user.student_id,
        "role": user.role,
        "department": user.department,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
