from fastapi import APIRouter,Depends,HTTPException,status
from api.schemas.auth import SignUpRequest, SignUpResponse, UserListResponse, UserResponse
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import User
from api.helper.token_helper import password_hashing
from typing import List

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
    )

@router.post('/signup', response_model=SignUpResponse)
async def signup(user_data:SignUpRequest, db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if db.query(User).filter(User.username==user_data.username).first():
        raise  HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if user_data.role in ["user","admin",""]:
        if user_data.role=="":
            user_data.role="user"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect role"
        )
    
    hashed_password = password_hashing(user_data.password)
    if not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error hashing password"
        )
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return SignUpResponse(
            message="User registered successfully. Please login to get access token.",
            user=user
        )
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(error)}"
        )
