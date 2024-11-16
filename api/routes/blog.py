from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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
    """Check if user has permission to modify the blog"""
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        print("tokne--->",user_data.get("sub"),"     ",str(blog.user_id))
        # Check if user is admin or blog owner
        is_admin = user_data.get("role") == "admin"
        is_owner = str(blog.user_id) == user_data.get("sub")
        
        if not (is_admin or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this blog. Only the blog owner or admin can modify it."
            )
        
        return blog
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking blog permissions: {str(e)}"
        )

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
    title: str = Form(None, description="Updated blog title"),
    description: str = Form(None, description="Updated blog description"),
    image: UploadFile = File(None, description="Updated blog image"),
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """
    Update a blog post. Only the blog owner or admin can update it.
    """
    try:
        # First check permission
        blog = await check_blog_permission(blog_id, token_data, db)
        
        # Track if any changes were made
        changes_made = False
        
        # Validate and update fields
        if title is not None and title.strip():
            if len(title) > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title must be 100 characters or less"
                )
            blog.title = title.strip()
            changes_made = True
            
        if description is not None and description.strip():
            blog.description = description.strip()
            changes_made = True
            
        # Handle image upload if provided
        if image and image.filename:
            # Validate image
            if not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be an image"
                )
                
            # Delete old image if exists
            if blog.image_url:
                await delete_image(blog.image_url)
                
            # Upload new image
            blog.image_url = await upload_image(image)
            changes_made = True
            
        if not changes_made:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes provided for update"
            )
            
        db.commit()
        db.refresh(blog)
        return blog
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
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

@router.patch("/{blog_id}/like", response_model=BlogResponse)
async def toggle_like_blog(
    blog_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """
    Toggle like/unlike for a blog post.
    - If user hasn't liked the blog: adds like and user to like_user list
    - If user has already liked: removes like and user from like_user list
    """
    try:
        # Get the blog
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Get current user's ID
        current_user_id = str(token_data["sub"])
        
        # Initialize like_user list if None
        if blog.like_user is None:
            blog.like_user = []
        
        # Check if user has already liked
        if current_user_id in blog.like_user:
            # Unlike: Remove user and decrease count
            blog.like_user.remove(current_user_id)
            blog.like_count = max(0, blog.like_count - 1)  # Ensure count doesn't go below 0
        else:
            # Like: Add user and increase count
            blog.like_user.append(current_user_id)
            blog.like_count = blog.like_count + 1
        
        db.commit()
        db.refresh(blog)
        return blog
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling blog like: {str(e)}"
        )

# Add this route to get like status for current user
@router.get("/{blog_id}/like-status", response_model=dict)
async def get_blog_like_status(
    blog_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """
    Get the like status of the blog for the current user
    Returns:
    - liked: boolean indicating if current user has liked the blog
    - like_count: total number of likes
    """
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        current_user_id = str(token_data["sub"])
        is_liked = current_user_id in (blog.like_user or [])
        
        return {
            "liked": is_liked,
            "like_count": blog.like_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting blog like status: {str(e)}"
        ) 