from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.db import Base, engine
from api.routes.auth import router as auth_router
from api.routes.blog import router as blog_router
from api.routes.comment import router as comment_router
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from config import get_settings

# Load settings
settings = get_settings()

# Custom authentication middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = [
            "/", "/docs", "/openapi.json", "/redoc",
            "/auth/login", "/auth/signup"
        ]
        if request.url.path in public_paths:
            return await call_next(request)

        if not request.headers.get("Authorization"):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )

        return await call_next(request)

# Initialize the app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# OAuth2 Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="This is the API documentation for BlogZ4, demonstrating token-only authentication in Swagger.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.add_middleware(AuthMiddleware)

# Database setup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    raise RuntimeError(f"Database initialization failed: {e}")

# Include routers
app.include_router(auth_router)
app.include_router(blog_router)
app.include_router(comment_router)

# Root route
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the EchoBlog",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }

# Main entry point
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True  # Enable auto-reload for development
    )
