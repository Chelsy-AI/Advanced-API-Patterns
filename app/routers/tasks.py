from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Task
@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Read all tasks with pagination
@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks

# Read single task
@router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update Task
@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

# Delete Task
@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return

import httpx
from fastapi import BackgroundTasks

@router.get("/external-joke")
async def get_joke():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://official-joke-api.appspot.com/random_joke")
        data = response.json()
    return data
