from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from scheme import UserRegistration, UserLogin
from models import Users

router = APIRouter()

@router.post("/register")
async def register(
    register: UserRegistration,
    db:Annotated[Session, Depends(get_db)]
):
    reg = Users(email=register.email, password=register.password, username=register.username)
    db.add(reg)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(
    login: UserLogin,
    db: Annotated[Session, Depends(get_db)]
):
    log = db.query(Users).filter(Users.email == login.email).first()
    if not log:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "User logged in successfully"}