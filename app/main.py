from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, Base, engine
from . import models
from .schemas import UserCreate, UserLogin, PasswordChange, UserResponse
from .auth import hash_password, verify_password, create_access_token, verify_token

app = FastAPI()

Base.metadata.create_all(bind=engine)


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
    
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": str(db_user.id), "email": db_user.email}
    )
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(db_user.id),
        "username": db_user.username
    }

@app.put("/users/password")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    username = token_data.get("sub")
    
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password_data.old_password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    db_user.password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@app.delete("/users/me")
def delete_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    username = token_data.get("sub")
    
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(credentials.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}