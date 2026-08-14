from fastapi import FastAPI, Depends, HTTPException
from pytest import Session
from authorization import router as authorization_router, auth
from database import engine, Base, get_db
from models import Users, Message
from typing import Annotated
from scheme import MessageSchema
from dependencies import current_user
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/me", dependencies=[Depends(auth.access_token_required)])
async def read_me():
    return {"message": "Hello, World!"}

@app.post('/message', dependencies=[Depends(auth.access_token_required)], response_model=None)
async def send_message(
    message: MessageSchema,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_message = Message(user_id=user.id, message=message.message)
    db.add(new_message)
    db.commit()
    return {"message": "Message sent successfully"}

@app.delete('/message/{message_id}', dependencies=[Depends(auth.access_token_required)], response_model=None)
async def delete_message(
    message_id: int,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)   
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    message = db.query(Message).filter(Message.id == message_id, Message.user_id == user.id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}

app.include_router(authorization_router)
