from fastapi import FastAPI, HTTPException, Depends, Security, Response
from sqlalchemy.orm import Session
from .database import get_db, init_db
from . import models
from .schemas import UserCreate, UserLogin, PasswordChange, UserDelete, UserResponse
from .auth import hash_password, verify_password, create_access_token, verify_token
from .logger import logger

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()
    logger.info("User service started")

@app.post("/users/register", response_model=UserResponse)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for username: {user.username}")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        logger.warning(f"Registration failed: Username '{user.username}' already exists")
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        logger.warning(f"Registration failed: Email '{user.email}' already registered")
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
    logger.info(f"User registered successfully: {user.username} (ID: {new_user.id})")
    return new_user

@app.post("/users/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: {user.username}")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        logger.warning(f"Login failed: Invalid credentials for username '{user.username}'")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": str(db_user.id), "email": db_user.email}
    )
    
    logger.info(f"Login successful for user: {user.username} (ID: {db_user.id})")
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
    logger.info(f"Password change request for user: {username}")
    
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        logger.error(f"Password change failed: User '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password_data.old_password, db_user.password):
        logger.warning(f"Password change failed: Invalid old password for user '{username}'")
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    db_user.password = hash_password(password_data.new_password)
    db.commit()
    logger.info(f"Password changed successfully for user: {username}")
    return {"message": "Password changed successfully"}

@app.delete("/users/me")
def delete_user(
    credentials: UserDelete,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    username = token_data.get("sub")
    logger.info(f"User deletion request for: {username}")
    
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        logger.error(f"User deletion failed: User '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(credentials.password, db_user.password):
        logger.warning(f"User deletion failed: Invalid credentials for user '{username}'")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    db.delete(db_user)
    db.commit()
    logger.info(f"User deleted successfully: {username}")
    return {"message": "User deleted successfully"}

# @app.get("/users/me")
# def get_current_user(
#     db: Session = Depends(get_db),
#     token_data: dict = Depends(verify_token)
# ):
#     username = token_data.get("sub")
#     logger.info(f"User info request for: {username}")
    
#     db_user = db.query(models.User).filter(models.User.username == username).first()
#     if not db_user:
#         logger.error(f"User info request failed: User '{username}' not found")
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return {"username": db_user.username, "email": db_user.email}

@app.get("/validate-token")
def validate_token(
    response: Response,
    payload: dict = Security(verify_token),
    db: Session = Depends(get_db)
):
    """
    Check if a user is authenticated.
    """
    response.headers["X-User-Id"] = str(payload.get("user_id"))
    response.headers["X-User-Email"] = str(payload.get("email"))
    return {"status": "valid"}