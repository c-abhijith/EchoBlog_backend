from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import User
from api.schemas.user import UserProfileResponse, UserProfileUpdate
from api.helper.auth_bearer import verify_token
from api.helper.cloudinary_helper import upload_image, delete_image
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Get current user's profile"""
    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    bio: Optional[str] = Form(None, description="User bio"),
    title: Optional[str] = Form(None, description="User title/designation"),
    twitter_url: Optional[str] = Form(None, description="Twitter profile URL"),
    instagram_url: Optional[str] = Form(None, description="Instagram profile URL"),
    linkedin_url: Optional[str] = Form(None, description="LinkedIn profile URL"),
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """
    Update user profile information
    - **bio**: Optional user biography
    - **title**: Optional user title or designation
    - **twitter_url**: Optional Twitter profile URL
    - **instagram_url**: Optional Instagram profile URL
    - **linkedin_url**: Optional LinkedIn profile URL
    """
    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    if bio is not None:
        user.bio = bio
    if title is not None:
        user.title = title
    if twitter_url is not None:
        user.twitter_url = twitter_url
    if instagram_url is not None:
        user.instagram_url = instagram_url
    if linkedin_url is not None:
        user.linkedin_url = linkedin_url
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.patch(
    "/profile/image", 
    response_model=UserProfileResponse,
    summary="Update profile image",
    description="Upload a new profile image (jpg, jpeg, png, gif, < 3MB)"
)
async def update_profile_image(
    image: UploadFile = File(
        ...,
        description="Profile image file (jpg, jpeg, png, gif, < 3MB)",
        media_type="image/*"
    ),
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """
    Upload a new profile image:
    - Accepts jpg, jpeg, png, gif formats
    - Maximum file size: 3MB
    - Previous image will be deleted if exists
    """
    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Delete old image if exists
        if hasattr(user, 'profile_image') and user.profile_image:
            await delete_image(user.profile_image)
        
        # Upload new image
        image_url = await upload_image(image, folder="profiles")
        user.profile_image = image_url
        
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile image: {str(e)}"
        ) 