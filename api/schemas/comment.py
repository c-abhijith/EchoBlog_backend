from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    comment: str

class CommentUpdate(BaseModel):
    comment: str

class CommentResponse(BaseModel):
    id: UUID4
    comment: str
    blog_id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    user_name: str  # Include user's name in response
    
    class Config:
        from_attributes = True 