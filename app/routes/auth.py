from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any
from ..auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_superuser,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password
)
from ..database import get_db, create_superuser
from ..models import User
from passlib.context import CryptContext
import secrets
import logging
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    department: str | None = None
    role: str | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    is_superuser: bool
    department: str | None
    role: str | None

    class Config:
        from_attributes = True

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """Login endpoint to get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """Register a new user (superuser only)."""
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = User(
        email=str(user_data.email),  # Convert EmailStr to str
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        department=user_data.department,
        role=user_data.role,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update current user information."""
    # Check if email is taken
    if str(user_data.email) != current_user.email:  # Convert EmailStr to str
        if db.query(User).filter(User.email == str(user_data.email)).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if username is taken
    if user_data.username != current_user.username:
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user using SQLAlchemy update
    db.query(User).filter(User.id == current_user.id).update({
        "email": str(user_data.email),  # Convert EmailStr to str
        "username": user_data.username,
        "full_name": user_data.full_name,
        "department": user_data.department,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password) if user_data.password else current_user.hashed_password
    })
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/create-superuser", response_model=UserResponse)
async def create_superuser_endpoint(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Create a new superuser (only available during initial setup)."""
    try:
        superuser = create_superuser(
            email=str(user_data.email),  # Convert EmailStr to str
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return superuser
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/api/auth/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Refresh access token."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/api/auth/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "api_key": current_user.api_key
    } 