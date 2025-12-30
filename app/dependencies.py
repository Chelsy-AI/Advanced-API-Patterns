# app/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import get_current_user, require_admin
from app.utils import rate_limiter

# ----------------------------
# Database dependency
# ----------------------------
def get_db() -> Session:
    """
    Provide a SQLAlchemy session for request lifecycle.
    Ensures session is closed after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# User authentication dependency
# ----------------------------
def get_user(token: str = Depends(get_current_user)):
    """
    Returns the current authenticated user.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or missing token")
    return token

# ----------------------------
# Admin role dependency
# ----------------------------
def get_admin(user=Depends(get_user)):
    """
    Ensures the current user has admin privileges.
    """
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin privileges required")
    return user

# ----------------------------
# Rate limiting dependency
# ----------------------------
def rate_limit(request: Request):
    """
    Rate limit requests per client IP.
    """
    try:
        rate_limiter(request)
    except HTTPException as e:
        raise e
