"""
SafeCampus AI — Authentication Router
======================================
POST /api/auth/register → Register new campus user
POST /api/auth/login    → Login and retrieve JWT/bearer token
GET  /api/auth/me       → Current user profile
"""

import hashlib
import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter()

# Simple secret salt for password hashing in research environment
_SECRET_SALT = os.environ.get("AUTH_SECRET_SALT", "safecampus_salt_2026")
# In-memory token store for session verification (zero-overhead)
_ACTIVE_SESSIONS: dict[str, int] = {}


def _hash_password(password: str) -> str:
    return hashlib.sha256(f"{password}:{_SECRET_SALT}".encode()).hexdigest()


def _verify_password(password: str, hashed: str) -> bool:
    return _hash_password(password) == hashed


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new campus user",
)
async def register_user(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Registers a new campus user (student/faculty/visitor) in SQLite."""
    # Check if username or email already exists
    existing = await db.execute(
        select(User).where((User.username == request.username) | (User.email == request.email))
    )
    if existing.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered.",
        )

    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=_hash_password(request.password),
        is_active=True,
        is_admin=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = secrets.token_hex(24)
    _ACTIVE_SESSIONS[token] = new_user.id

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active,
            is_admin=new_user.is_admin,
            role=request.role or "student",
            accessibility_need=request.accessibility_need,
        ),
        message="Registration successful.",
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
)
async def login_user(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Authenticates campus user via email and password."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()

    if user is None or not _verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = secrets.token_hex(24)
    _ACTIVE_SESSIONS[token] = user.id

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_admin=user.is_admin,
            role="student",
        ),
        message="Login successful.",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Returns profile for currently authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        # Return default guest user if no auth token supplied
        return UserResponse(
            id=0,
            username="campus_guest",
            email="guest@safecampus.edu",
            is_active=True,
            is_admin=False,
            role="guest",
        )

    token = authorization.split(" ", 1)[1]
    user_id = _ACTIVE_SESSIONS.get(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token.",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        role="student",
    )
