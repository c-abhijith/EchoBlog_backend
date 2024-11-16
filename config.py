import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8000'))
    SERVER_WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./blogz4.db")

@lru_cache
def get_settings() -> Settings:
    return Settings()