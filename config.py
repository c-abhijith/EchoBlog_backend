import os
from functools import lru_cache
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv('APP_NAME', 'FastAPi Docs')
    APP_VERSION: str = os.getenv('APP_VERSION', '0.0.1')
    DEBUG = os.getenv('DEBUG', '0.0.1')
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8000'))
    SERVER_WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    DATABASE_URL:str = os.getenv("DATABASE_URL","")
    
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() for origin in 
        os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").replace("[", "").replace("]", "").split(",")
    ]
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

@lru_cache
def get_settings() -> Settings:
    return Settings()