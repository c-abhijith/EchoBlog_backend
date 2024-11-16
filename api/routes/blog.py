from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import Blog, User, UserRole
from api.schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from api.helper.auth_bearer import verify_token
from api.helper.cloudinary_helper import upload_image, delete_image
from typing import List, Optional
from uuid import UUID

router = APIRouter(
    prefix="/blogs",
    tags=["blogs"]
)

async def check_blog_permission(blog_id: UUID, user_data: dict, db: Session):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    if user_data["role"] != "admin" and str(blog.user_id) != user_data["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this blog"
        )
    return blog

@router.post("/", response_model=BlogResponse)
async def create_blog(
    title: str,
    description: str,
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        # Handle image upload if provided
        image_url = None
        if image:
            image_url = await upload_image(image)
        
        blog = Blog(
            title=title,
            description=description,
            image_url=image_url,
            user_id=token_data["sub"]
        )
        
        db.add(blog)
        db.commit()
        db.refresh(blog)
        return blog
        
    except Exception as e:
        if 'image_url' in locals() and image_url:
            await delete_image(image_url)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating blog: {str(e)}"
        )

@router.get("/", response_model=List[BlogResponse])
async def get_blogs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    blogs = db.query(Blog).offset(skip).limit(limit).all()
    return blogs

@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(
    blog_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    return blog

@router.put("/{blog_id}", response_model=BlogResponse)
async def update_blog(
    blog_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    blog = await check_blog_permission(blog_id, token_data, db)
    
    try:
        # Handle image upload if provided
        if image:
            # Delete old image if exists
            if blog.image_url:
                await delete_image(blog.image_url)
            # Upload new image
            blog.image_url = await upload_image(image)
        
        if title is not None:
            blog.title = title
        if description is not None:
            blog.description = description
            
        db.commit()
        db.refresh(blog)
        return blog
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating blog: {str(e)}"
        )

@router.delete("/{blog_id}")
async def delete_blog(
    blog_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    blog = await check_blog_permission(blog_id, token_data, db)
    
    try:
        # Delete image from Cloudinary if exists
        if blog.image_url:
            await delete_image(blog.image_url)
            
        db.delete(blog)
        db.commit()
        return {"message": "Blog deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting blog: {str(e)}"
        ) 