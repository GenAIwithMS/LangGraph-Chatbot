from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from pydantic import BaseModel
import bcrypt as _bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import DatabaseConfig, User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET", "opengpt-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    username: str
    user_id: int


class UserResponse(BaseModel):
    id: int
    username: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _resolve_user(token_str: Optional[str]) -> Optional[User]:
    if not token_str:
        return None
    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            return None
    except JWTError:
        return None
    session = DatabaseConfig.create_session()
    try:
        return session.query(User).filter_by(id=user_id).first()
    finally:
        session.close()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Query(None)
) -> Optional[User]:
    token_str = token or (credentials.credentials if credentials else None)
    return _resolve_user(token_str)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    session = DatabaseConfig.create_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        session.close()


@auth_router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    if len(req.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    session = DatabaseConfig.create_session()
    try:
        existing = session.query(User).filter_by(username=req.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        user = User(
            username=req.username,
            password_hash=_bcrypt.hashpw(req.password.encode(), _bcrypt.gensalt()).decode()
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = create_access_token({"user_id": user.id, "username": user.username})
        return TokenResponse(token=token, username=user.username, user_id=user.id)
    finally:
        session.close()


@auth_router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    session = DatabaseConfig.create_session()
    try:
        user = session.query(User).filter_by(username=req.username).first()
        if not user or not _bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_access_token({"user_id": user.id, "username": user.username})
        return TokenResponse(token=token, username=user.username, user_id=user.id)
    finally:
        session.close()


@auth_router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse(id=user.id, username=user.username)
