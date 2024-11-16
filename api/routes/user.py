from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session, joinedload
from api.db import get_db
from api.models import User, Blog
from api.schemas.user import UserProfileResponse
from api.helper.auth_bearer import verify_token
from typing import Optional, List
from uuid import UUID

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/profile", response_model=UserProfileResponse)
async def get_own_profile(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Get current user's profile with their blogs"""
    try:
        # Get user with blogs
        user = db.query(User).options(
            joinedload(User.blogs)
        ).filter(
            User.id == token_data["sub"]
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "title": user.title,
            "twitter_url": user.twitter_url,
            "instagram_url": user.instagram_url,
            "linkedin_url": user.linkedin_url,
            "profile_image": user.profile_image,
            "created_at": user.created_at,
            "blogs": user.blogs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Get a specific user's profile with their blogs"""
    try:
        # Get user with blogs
        user = db.query(User).options(
            joinedload(User.blogs)
        ).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "title": user.title,
            "twitter_url": user.twitter_url,
            "instagram_url": user.instagram_url,
            "linkedin_url": user.linkedin_url,
            "profile_image": user.profile_image,
            "created_at": user.created_at,
            "blogs": user.blogs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        ) 