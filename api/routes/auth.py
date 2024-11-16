from fastapi import APIRouter,Depends,HTTPException,status
from api.schemas.auth import SignUpRequest, SignUpResponse,Token,Login
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import User
from api.helper.token_helper import password_hashing,password_verify,create_access_token,create_refresh_token
from datetime import timedelta
from config import get_settings

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
    )

settings = get_settings()

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
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=password_hashing(user_data.password),
        role=user_data.role
    )
    
    try:
        print("--------------------------")
        db.add(user)
        db.commit()
        db.refresh(user)
        print("---------------------------")
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

@router.post('/login', response_model=Token)
async def login(user_data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    print(db.query(User).all())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email"
        )
    
    password_correct = password_verify(user_data.password, user.password)
    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        subject=str(user.id)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }