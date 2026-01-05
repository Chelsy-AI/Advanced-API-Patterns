# app/utils.py

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from typing import Optional
import jwt
import os
import logging

# ------------------------------
# Optional Redis client
# ------------------------------
try:
    from app.database import redis_client
except Exception:
    redis_client = None

logger = logging.getLogger(__name__)

# ------------------------------
# JWT and Password Config
# ------------------------------

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-dev-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ------------------------------
# Password Utilities
# ------------------------------

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------------
# JWT Utilities
# ------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[int] = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    Create a JWT access token.
    IMPORTANT: caller must include `sub` in data for OAuth2 compatibility.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT token. Returns payload or None if invalid."""
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        logger.warning("JWT expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT")
        return None

# ------------------------------
# Rate Limiter (Redis optional)
# ------------------------------

RATE_LIMIT = 5        # max requests
RATE_PERIOD = 60      # seconds

def rate_limiter(request: Request):
    """
    Simple IP-based rate limiter using Redis.
    If Redis is unavailable, requests are allowed.
    """
    if redis_client is None:
        return

    if not request.client:
        return

    client_ip = request.client.host
    key = f"rate:{client_ip}"

    try:
        current = redis_client.get(key)

        if current and int(current) >= RATE_LIMIT:
            ttl = redis_client.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds"
            )

        pipe = redis_client.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, RATE_PERIOD)
        pipe.execute()

    except HTTPException:
        raise
    except Exception as e:
        # Never fail auth because Redis is down
        logger.warning(f"Rate limiter skipped: {e}")
        return

# ------------------------------
# Custom API Exception
# ------------------------------

class APIException(HTTPException):
    """Custom exception for consistent API error responses."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(
            status_code=status_code,
            detail={"error": detail}
        )
