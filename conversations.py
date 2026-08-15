from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pytest import Session
from authorization import auth
from database import get_db
from models import Users, Message
from typing import Annotated
from scheme import SentMessage
from dependencies import current_user

router = APIRouter()

@router.post('/conversations', dependencies=[Depends(auth.access_token_required)], response_model=None)
async def send_message(
    conversations: SentMessage,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    receiver = db.query(Users).filter(Users.username == conversations.receiver_message).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    new_conversations = Message(
        user_id=user.id,
        message=conversations.message,
        receiver_id=receiver.id,
        created_at=datetime.now())

    db.add(new_conversations)
    db.commit()
    db.refresh(new_conversations)
    return {"message": "Message sent successfully"}

@router.get("/conversations", dependencies=[Depends(auth.access_token_required)])
async def read_messages(
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    conversations = db.query(Message).filter(Message.receiver_id == user.id).all()
    return {"messages": conversations}

@router.get("/conversations/{conversations_id}", dependencies=[Depends(auth.access_token_required)])
async def read_messages(
    conversations_id: int,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    conversations = db.query(Message).filter(Message.receiver_id == user.id, Message.user_id == conversations_id).first()
    if not conversations:
            raise HTTPException(status_code=404, detail="Message not found")
    return {"messages": conversations}


@router.delete('/conversations/{conversations_id}', dependencies=[Depends(auth.access_token_required)], response_model=None)
async def delete_conversations(
    conversations_id: int,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)   
):
    user = db.query(Users).filter(Users.id == user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    conversations = db.query(Message).filter(Message.id == conversations_id).first()
    if not conversations:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(conversations)
    db.commit()
    return {"message": "Message deleted successfully"}

