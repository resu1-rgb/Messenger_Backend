from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    email: EmailStr
    password: str

class MessageSchema(BaseModel):
    message: str