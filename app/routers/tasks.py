# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.dependencies import get_db, get_user, rate_limit
import httpx

router = APIRouter(prefix="/tasks", tags=["tasks"])

# ----------------------------
# Create Task
# ----------------------------
@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_user),
    request: Request = Depends(rate_limit)
):
    try:
        db_task = models.Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Read All Tasks
# ----------------------------
@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_user),
    request: Request = Depends(rate_limit)
):
    try:
        return db.query(models.Task).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Read Single Task
# ----------------------------
@router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_user),
    request: Request = Depends(rate_limit)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ----------------------------
# Update Task
# ----------------------------
@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_user),
    request: Request = Depends(rate_limit)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


# ----------------------------
# Delete Task
# ----------------------------
@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_user),
    request: Request = Depends(rate_limit)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return


# ----------------------------
# External API Example
# ----------------------------
@router.get("/external-joke")
async def get_joke(request: Request = Depends(rate_limit)):
    """
    Fetch a random joke from external API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://official-joke-api.appspot.com/random_joke")
            response.raise_for_status()
            data = response.json()
        return data
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
