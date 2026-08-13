from fastapi import APIRouter
from pydantic import BaseModel
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

router = APIRouter()

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    pwd: Mapped[str] = mapped_column(nullable=True)