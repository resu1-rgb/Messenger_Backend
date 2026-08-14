from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import ForeignKey
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

router = APIRouter()

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    pwd: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(default='user')

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column()