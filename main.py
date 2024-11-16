from fastapi import FastAPI
from config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from api.db import Base, engine
from api.routes.auth import router as auth_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create tables
print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {str(e)}")
    raise

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the EchoBlog",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }

if __name__=='__main__':
    import uvicorn
    uvicorn.run("main:app",
                host=settings.SERVER_HOST,
                port=settings.SERVER_PORT,
                reload=settings.SERVER_WORKERS
                )
    