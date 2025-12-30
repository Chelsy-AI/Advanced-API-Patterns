from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from fastapi import Request, HTTPException, status
import time
from app.database import redis_client


SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create JWT access token
def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decode and verify JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

RATE_LIMIT = 5  # max requests
RATE_PERIOD = 60  # seconds

def rate_limiter(request: Request):
    client_ip = request.client.host
    key = f"rate:{client_ip}"
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


class APIException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail={"error": detail})
