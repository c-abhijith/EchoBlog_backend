from pydantic import BaseModel, UUID4, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class UserProfileResponse(BaseModel):
    id: UUID4
    username: str
    email: str
    bio: Optional[str] = None
    title: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    title: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None 