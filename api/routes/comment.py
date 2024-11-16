from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import Comment, Blog, User
from api.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from api.helper.auth_bearer import verify_token
from typing import List
from uuid import UUID

router = APIRouter(
    prefix="/blogs/{blog_id}/comments",
    tags=["comments"]
)

@router.post("/", response_model=CommentResponse)
async def create_comment(
    blog_id: UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Create a new comment on a blog post"""
    try:
        # Check if blog exists
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )

        # Create comment
        comment = Comment(
            comment=comment_data.comment,
            blog_id=blog_id,
            user_id=token_data["sub"]
        )
        
        # Update blog's comment count
        blog.comment_count += 1
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        # Add user_name to response
        setattr(comment, 'user_name', token_data["username"])
        
        return comment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating comment: {str(e)}"
        )

@router.get("/", response_model=List[CommentResponse])
async def get_blog_comments(
    blog_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Get all comments for a blog post"""
    try:
        comments = db.query(Comment)\
            .join(User)\
            .filter(Comment.blog_id == blog_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
            
        # Add user_name to each comment
        for comment in comments:
            setattr(comment, 'user_name', comment.user.username)
            
        return comments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching comments: {str(e)}"
        )

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    blog_id: UUID,
    comment_id: UUID,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Update a comment (only owner can update)"""
    try:
        comment = db.query(Comment)\
            .filter(Comment.id == comment_id, Comment.blog_id == blog_id)\
            .first()
            
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
            
        # Check if user is comment owner
        if str(comment.user_id) != token_data["sub"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment"
            )
            
        comment.comment = comment_data.comment
        db.commit()
        db.refresh(comment)
        
        # Add user_name to response
        setattr(comment, 'user_name', token_data["username"])
        
        return comment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating comment: {str(e)}"
        )

@router.delete("/{comment_id}")
async def delete_comment(
    blog_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Delete a comment (only owner or admin can delete)"""
    try:
        comment = db.query(Comment)\
            .filter(Comment.id == comment_id, Comment.blog_id == blog_id)\
            .first()
            
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
            
        # Check if user is comment owner or admin
        is_admin = token_data.get("role") == "admin"
        is_owner = str(comment.user_id) == token_data["sub"]
        
        if not (is_admin or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )
            
        # Update blog's comment count
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if blog:
            blog.comment_count = max(0, blog.comment_count - 1)
            
        db.delete(comment)
        db.commit()
        
        return {"message": "Comment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting comment: {str(e)}"
        ) 