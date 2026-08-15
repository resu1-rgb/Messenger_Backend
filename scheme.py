from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    email: EmailStr
    password: str

class SentMessage(BaseModel):
    message: str
    receiver_message: str
