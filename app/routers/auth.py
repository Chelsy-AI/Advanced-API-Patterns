# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import models, schemas, utils
from app.dependencies import get_db, get_user, get_admin

router = APIRouter(prefix="/auth", tags=["auth"])

# ----------------------------
# Register User
# ----------------------------
@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(models.User).filter(models.User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = utils.hash_password(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Login User
# ----------------------------
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.username == form_data.username).first()
        if not user or not utils.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = utils.create_access_token({"sub": user.username, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Example Admin-only route
# ----------------------------
@router.get("/admin", response_model=schemas.UserResponse)
def admin_route(admin: models.User = Depends(get_admin)):
    """
    Example endpoint restricted to admin users
    """
    return admin
