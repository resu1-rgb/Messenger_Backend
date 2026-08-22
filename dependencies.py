from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from authorization import auth
from typing import Annotated
from pwdlib import PasswordHash

def current_user(payload: Annotated[Session, Depends(auth.access_token_required)]):
    user_id = payload.sub
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = int(user_id)
    return user_id

password_hasher = PasswordHash.recommended()

def password_hash(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)

