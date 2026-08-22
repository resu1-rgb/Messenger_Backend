from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from scheme import UserRegistration, UserLogin
from models import Users
from auth_config import auth
from dependencies import password_hash, verify_password

router = APIRouter()

@router.post("/auth/register")
async def register(
    register: UserRegistration,
    db: Annotated[Session, Depends(get_db)]
):
    reg = Users(
        email = register.email,  
        username = register.username,
        pwd = password_hash(register.password),
        role = 'user'
    )
    db.add(reg)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/auth/login")
async def login(
    login: UserLogin,
    db: Annotated[Session, Depends(get_db)]
):
    log = db.query(Users).filter(Users.email == login.email).first()

    if log and verify_password(login.password, log.pwd):
        token = auth.create_access_token(uid=str(log.id))
        return {"token": token}
    raise HTTPException(status_code=400, detail="Invalid username or password")

