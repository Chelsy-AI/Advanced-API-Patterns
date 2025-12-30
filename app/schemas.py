from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime, timezone

# ------------------------------
# Task Schemas
# ------------------------------

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    completed: bool
    created_at: datetime

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }


# ------------------------------
# User Schemas
# ------------------------------

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)  # Enforce strong password

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }


# ------------------------------
# Token Schema
# ------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str
