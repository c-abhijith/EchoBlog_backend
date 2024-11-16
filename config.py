import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    APP_NAME: str = os.getenv('APP_NAME', 'FastAPi Docs')
    APP_VERSION: str = os.getenv('APP_VERSION', '0.0.1')
    DEBUG=os.getenv('DEBUG', '0.0.1')
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8000'))
    SERVER_WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./blogz4.db")

@lru_cache
def get_settings() -> Settings:
    return Settings()