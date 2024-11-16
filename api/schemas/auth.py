from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime

class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: str
    role: str
    bio: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class SignUpResponse(BaseModel):
    message: str
    user: UserResponse

class Token(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str
    
class Login(BaseModel):
    email:str
    password:str
    