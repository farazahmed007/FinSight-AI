from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import sqlite3
import uuid

from database import get_db_connection
from services.auth_service import AuthService
from middleware.auth import require_auth

auth_bp = APIRouter()

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str

@auth_bp.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user: UserRegister):
    if not user.username or len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
    if not user.password or len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Username already registered")
        
    user_id = str(uuid.uuid4())
    password_hash = AuthService.get_password_hash(user.password)
    
    try:
        cursor.execute(
            "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
            (user_id, user.username, password_hash)
        )
        conn.commit()
    except Exception:
        conn.close()
        raise HTTPException(status_code=500, detail="Failed to create user")
        
    conn.close()
    return {"id": user_id, "username": user.username}

@auth_bp.post("/login", response_model=TokenResponse, tags=["Auth"])
def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not db_user['password_hash']:
        # Return generic failure response
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    if not AuthService.verify_password(user.password, db_user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    access_token = AuthService.create_access_token(data={"sub": db_user['id'], "username": db_user['username']})
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_bp.get("/me", response_model=UserResponse, tags=["Auth"])
def get_me(user_id: str = Depends(require_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"id": db_user['id'], "username": db_user['username']}
