from fastapi import Depends, HTTPException
from pytest import Session
from authorization import auth
from typing import Annotated

def current_user(payload: Annotated[Session, Depends(auth.access_token_required)]):
    user_id = payload.sub
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = int(user_id)
    return user_id
