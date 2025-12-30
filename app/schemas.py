from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

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

    class Config:
        orm_mode = True


# Input schemas
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)  # Enforce strong password
    
class UserLogin(BaseModel):
    username: str
    password: str

# Output schemas
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        orm_mode = True

# JWT token schema
class Token(BaseModel):
    access_token: str
    token_type: str
