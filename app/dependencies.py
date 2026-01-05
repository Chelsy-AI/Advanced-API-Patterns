# app/dependencies.py

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import time

from app.database import SessionLocal, redis_client
from app import models, utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

RATE_LIMIT = 5        # requests
RATE_PERIOD = 60      # seconds


# ----------------------------
# Database Dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Get Current User
# ----------------------------
def get_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = utils.decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# ----------------------------
# Admin-only Dependency
# ----------------------------
def get_admin(user: models.User = Depends(get_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


# ----------------------------
# Rate Limiting Dependency
# ----------------------------
def rate_limit(request: Request):
    """
    Redis-backed rate limiter.
    Fails open if Redis is unavailable (production-safe).
    """
    try:
        client_ip = request.client.host
        key = f"rate:{client_ip}"

        current = redis_client.get(key)

        if current and int(current) >= RATE_LIMIT:
            ttl = redis_client.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds",
                headers={
                    "Retry-After": str(ttl),
                    "X-RateLimit-Limit": str(RATE_LIMIT),
                    "X-RateLimit-Remaining": "0",
                },
            )

        pipe = redis_client.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, RATE_PERIOD)
        pipe.execute()

    except HTTPException:
        raise
    except Exception:
        # Redis is down → allow request (fail open)
        pass
