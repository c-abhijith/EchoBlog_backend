from fastapi import FastAPI, Request
from config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from api.db import Base, engine
from api.routes.auth import router as auth_router
from api.routes.blog import router as blog_router
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

settings = get_settings()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = [
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/auth/login",
            "/auth/signup"
        ]
        
        if request.url.path in public_paths:
            return await call_next(request)
            
        if not request.headers.get("Authorization"):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
            
        return await call_next(request)

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

app.add_middleware(AuthMiddleware)


try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    raise

app.include_router(auth_router)
app.include_router(blog_router)

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
    