from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, init_db
from . import models
from .schemas import UserCreate, UserLogin, PasswordChange, UserResponse
from .auth import hash_password, verify_password

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

@app.post("/users/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/users/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": db_user.id, "username": db_user.username}

@app.put("/users/{username}/password")
def change_password(username: str, password_data: PasswordChange, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password_data.old_password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    db_user.password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@app.delete("/users/{username}")
def delete_user(username: str, credentials: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(credentials.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}