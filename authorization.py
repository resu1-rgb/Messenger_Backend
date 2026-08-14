from typing import Annotated
import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from scheme import UserRegistration, UserLogin
from models import Users
from authx import AuthX, AuthXConfig
import bcrypt

load_dotenv()

config = AuthXConfig(
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
    JWT_ALGORITHM=os.getenv("JWT_ALGORITHM"),
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
router = APIRouter()

@router.post("/auth/register")
async def register(
    register: UserRegistration,
    db: Annotated[Session, Depends(get_db)]
):
    reg = Users(
        email = register.email,  
        username = register.username,
        pwd = bcrypt.hashpw(register.password.encode(), bcrypt.gensalt(prefix=b"2b")).decode('utf-8'),
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

    if log and bcrypt.checkpw(login.password.encode(), log.pwd.encode('UTF-8')):
        token = auth.create_access_token(uid=str(log.id))
        return {"token": token}
    raise HTTPException(status_code=400, detail="Invalid username or password")

