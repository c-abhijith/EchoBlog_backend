from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class BlogCreate(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class BlogResponse(BaseModel):
    id: UUID4
    title: str
    description: str
    image_url: Optional[str]
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime
    user_id: UUID4
    is_active: bool = True
    
    class Config:
        from_attributes = True

class BlogListResponse(BaseModel):
    total: int
    blogs: List[BlogResponse]
    
    class Config:
        from_attributes = True

class BlogWithUser(BlogResponse):
    user_name: str
    user_email: str
    
    class Config:
        from_attributes = True 