from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, Query
from sqlalchemy.orm import Session
from authorization import auth
from auth_config import config
from database import get_db
from models import Users, Message
from typing import Annotated
from scheme import SentMessage
from dependencies import current_user
import jwt

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

connected_clients = {}

@router.websocket("/ws/{user_id}")
async def ws(
    ws: WebSocket,
    db: Annotated[Session, Depends(get_db)],
    token: str = Query(...),
):
    await ws.accept()
    
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        await ws.close(code=1008)
        return


    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        await ws.close(code=1008)
        db.close()
        return

    connected_clients[user_id] = ws

    try:
        unread_message = db.query(Message).filter(Message.receiver_id == user_id, Message.is_read == False).order_by(Message.created_at).all()

        for msg in unread_message:
            await ws.send_json({
                'type': 'history',
                'from': msg.user_id,
                'message': msg.message,
                'created_at': msg.created_at.isoformat()
            })
            msg.is_read = True
        db.commit()

        while True:
            data = await ws.receive_json()

            receiver_id = data.get('receiver_id')
            message = data.get('message')

            if not receiver_id or not message:
                await ws.send_json({"error": "receiver_id and message are required"})
                continue

            new_message = Message(
                user_id=user_id,
                receiver_id=receiver_id,
                message=message,
                created_at=datetime.now()
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            if receiver_id in connected_clients:
                try:
                    await connected_clients[receiver_id].send_json({
                        'type': 'new_message',
                        'from': user_id,
                        'message': message,
                        'created_at': new_message.created_at.isoformat(),
                        'message_id': new_message.id
                    })

                except Exception:
                    pass

            await ws.send_json({
                'type': 'message_sent',
                'message_id': new_message.id,
                'receiver_id': receiver_id
            })  
            
    except Exception as e:
        print(f'Error {e}')
    finally:
        connected_clients.pop(user_id, None)
        db.close()

@router.get("/messages/history/{other_user_id}")
async def get_chat_history(
    other_user_id: int,
    db: Annotated[Session, Depends(get_db)],
    user = Depends(current_user)
):  
    
    messages = db.query(Message).filter(
        ((Message.user_id == user) & (Message.receiver_id == other_user_id)) |
        ((Message.user_id == other_user_id) & (Message.receiver_id == user))
    ).all()

    return messages

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

