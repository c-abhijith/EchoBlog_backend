from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext
from config import get_settings

settings = get_settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def password_hashing(password: str) -> str:
    return password_context.hash(password)

def password_verify(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(subject: Union[str, Any], username: str, email: str, role: str, expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expires_delta,
        "sub": str(subject),
        "username": username,
        "email": email,
        "role": role
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], username: str, email: str, role: str, expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(days=7)  
    
    to_encode = {
        "exp": expires_delta,
        "sub": str(subject),
        "username": username,
        "email": email,
        "role": role
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt