from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..db import get_db, engine
from ..db.models import User, Base
from ..security import create_token

# Ensure tables exist when module is imported
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth")


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=user.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=credentials.username).first()
    if not db_user or not pwd_context.verify(
        credentials.password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    role = db_user.role.value if hasattr(db_user.role, "value") else db_user.role
    token = create_token(str(db_user.id), role)
    return {"access_token": token, "token_type": "bearer"}
