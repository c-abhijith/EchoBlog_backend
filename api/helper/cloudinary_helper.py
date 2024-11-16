import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status
from typing import Optional
import os
from config import get_settings

settings = get_settings()

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def upload_image(file, folder: str = "blogs") -> Optional[str]:
    try:
        # Check file size (3MB = 3 * 1024 * 1024 bytes)
        MAX_SIZE = 3 * 1024 * 1024  # 3MB in bytes
        
        # Read the file into memory to check its size
        contents = await file.read()
        if len(contents) > MAX_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 3MB"
            )
            
        # Reset file pointer
        await file.seek(0)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            allowed_formats=['jpg', 'jpeg', 'png', 'gif'],
            resource_type="image"
        )
        
        return result['secure_url']
        
    except Exception as e:
        if "Invalid image file" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file. Please upload a valid image."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )

async def delete_image(image_url: str) -> bool:
    try:
        # Extract public_id from URL
        public_id = image_url.split('/')[-1].split('.')[0]
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception:
        return False 