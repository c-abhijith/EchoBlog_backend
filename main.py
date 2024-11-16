from fastapi import FastAPI
from config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

@app.get('/')
def index():
    return {"message":"Welcome to your blog application"}

if __name__=='__main__':
    import uvicorn
    uvicorn.run("main:app",
                host=settings.SERVER_HOST,
                port=settings.SERVER_PORT,
                reload=settings.SERVER_WORKERS
                )
    