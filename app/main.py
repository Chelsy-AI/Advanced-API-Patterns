import uuid
import json
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine, redis_client
from app.routers import tasks, auth

# -------------------------------------------------
# App Initialization
# -------------------------------------------------

app = FastAPI(
    title="Task Management API",
    description="Production-ready API with auth, rate limiting, and observability",
    version="1.0.0",
)

# -------------------------------------------------
# Database Initialization
# -------------------------------------------------

Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# CORS Configuration
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Structured Logging Setup
# -------------------------------------------------

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# -------------------------------------------------
# Request ID Middleware
# -------------------------------------------------

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            }
        )
    )

    return response

# -------------------------------------------------
# Global Exception Handler
# -------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        json.dumps(
            {
                "request_id": getattr(request.state, "request_id", None),
                "error": str(exc),
                "path": request.url.path,
            }
        )
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

# -------------------------------------------------
# Health Check Endpoints
# -------------------------------------------------

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.get("/health/detailed", tags=["Health"])
def detailed_health_check():
    try:
        # Database check
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        # Redis check
        redis_client.ping()

        return {
            "status": "ok",
            "database": "ok",
            "redis": "ok",
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": str(e),
        }

# -------------------------------------------------
# API Versioned Routers
# -------------------------------------------------

app.include_router(auth.router, prefix="/v1")
app.include_router(tasks.router, prefix="/v1")
