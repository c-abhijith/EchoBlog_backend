from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional, List
from datetime import datetime

class BlogInProfile(BaseModel):
    id: UUID4
    title: str
    description: str
    image_url: Optional[str]
    like_count: int
    comment_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: UUID4
    username: str
    email: str
    bio: Optional[str]
    title: Optional[str]
    twitter_url: Optional[str]
    instagram_url: Optional[str]
    linkedin_url: Optional[str]
    profile_image: Optional[str]
    created_at: datetime
    blogs: List[BlogInProfile] = []
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    title: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None 