from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db, init_db
from . import models

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/signup")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}