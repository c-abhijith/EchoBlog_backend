import uuid
import enum
from api.db import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,DateTime,Text,Boolean,String,Enum,Integer,ForeignKey,ARRAY

class UserRole(str,enum.Enum):
    USER = "user"
    ADMIN = "admin"

class BaseModel(Base):
    __abstract__=True
    
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    info = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    

class User(BaseModel):
    __tablename__="users"
    
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    username = Column(String(30),nullable=False,unique=True)
    email = Column(String(50),nullable=False,unique=True)
    password = Column(String(255),nullable=False)
    bio = Column(Text,nullable=True)
    title = Column(String(30),nullable=True)
    twitter_url = Column(String(200),nullable=True)
    instagram_url = Column(String(200),nullable=True)
    linkedin_url = Column(String(200),nullable=True)
    role = Column(Enum(UserRole),default=UserRole.USER,nullable=False)
    
    blogs = relationship("Blog",back_populates="user",cascade="all,delete-orphan")
    comments = relationship("Comment",back_populates="user")


class Blog(BaseModel):
    __tablename__ = 'blogs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    like_count = Column(Integer, default=0)
    like_user = Column(ARRAY(String), default=list)
    comment_count = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    user = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog", cascade="all, delete-orphan")
    
    
    
class Comment(BaseModel):
    __tablename__='comments'
    
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    comment = Column(Text,nullable=True)
    blog_id = Column(UUID(as_uuid=True),ForeignKey('blogs.id'),nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey('users.id'),nullable=False)
    
    blog = relationship("Blog", back_populates="comments")
    user = relationship("User", back_populates="comments")
    
    
    
    
    
    
    