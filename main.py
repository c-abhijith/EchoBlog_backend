from fastapi import FastAPI
from config import get_settings

app = FastAPI()
settings = get_settings()

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
    