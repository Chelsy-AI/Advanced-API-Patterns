from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models, schemas, database, utils

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register User
@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
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

# Login User
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = utils.create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = utils.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Role-based access dependency
def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
