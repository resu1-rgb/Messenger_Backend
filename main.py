from fastapi import FastAPI, Depends, HTTPException
from pytest import Session
from authorization import router as authorization_router, auth
from conversations import router as conversations_router
from database import engine, Base, get_db
from models import Users, Message
from typing import Annotated
from dependencies import current_user
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/users", dependencies=[Depends(auth.access_token_required)])
async def users(
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    users = db.query(Users).all()
    return {"users": users}

@app.get('/users/me', dependencies=[Depends(auth.access_token_required)])
async def get_my_profile(
     db: Annotated[Session, Depends(get_db)],
     user: Users = Depends(current_user)
):
     user = db.query(Users).filter(Users.id == user).first()
     if not user:
         raise HTTPException(status_code=404, detail="User not found")
     return user

@app.get("/users/{users_id}", dependencies=[Depends(auth.access_token_required)])
async def users_id(
    users_id: int,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    users = db.query(Message).filter(Message.user_id == users_id).first()
    if not users:
            raise HTTPException(status_code=404, detail="User not found")
    return {"users": users}

app.include_router(authorization_router)
app.include_router(conversations_router)

if __name__ == "__main__":
    uvicorn.run('main:app', port=8000, reload=True)