from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .models import User
from .schemas import PasswordChange, UserDelete
from .auth import hash_password, verify_password
from .logger import logger

app = FastAPI(
    docs_url="/docs/user",
    openapi_url="/openapi.json/user",
    redoc_url="/redoc/user"
)

@app.on_event("startup")
def startup():
    init_db()
    logger.info("User service started")

@app.put("/users/password")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    x_user_id: str = Header(None, alias="X-User-Id")
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"Password change request for user ID: {x_user_id}")
    
    db_user = db.query(User).filter(User.id == x_user_id).first()
    if not db_user:
        logger.error(f"Password change failed: User for ID: '{x_user_id}' not found")
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password_data.old_password, db_user.password):
        logger.warning(f"Password change failed: Invalid old password for user ID '{x_user_id}'")
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    db_user.password = hash_password(password_data.new_password)
    db.commit()
    logger.info(f"Password changed successfully for user ID: {x_user_id}")
    return {"message": "Password changed successfully"}

@app.delete("/users/me")
def delete_user(
    credentials: UserDelete,
    db: Session = Depends(get_db),
    x_user_id: str = Header(None, alias="X-User-Id")
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info(f"User deletion request for ID: {x_user_id}")
    
    db_user = db.query(User).filter(User.id == x_user_id).first()
    if not db_user:
        logger.error(f"User deletion failed: User for ID: '{x_user_id}' not found")
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(credentials.password, db_user.password):
        logger.warning(f"User deletion failed: Invalid credentials for user ID: '{x_user_id}'")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    db.delete(db_user)
    db.commit()
    logger.info(f"User deleted successfully: {x_user_id}")
    return {"message": "User deleted successfully"}

@app.get("/users/me")
def get_current_user(
    db: Session = Depends(get_db),
    x_user_id: str = Header(None, alias="X-User-Id")
):
    logger.info(f"User info request for ID: {x_user_id}")

    if not x_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_user = db.query(User).filter(User.id == x_user_id).first()
    if not db_user:
        logger.error(f"User info request failed: User for ID: '{x_user_id}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email
    }