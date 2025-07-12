from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import execute, health
from config import settings

app = FastAPI(
    title="Query Executor Service",
    description="SQL query execution service with JSON results",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, #tbd based on deployed envs
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(execute.router, prefix="/execute", tags=["execution"])

@app.get("/")
async def root():
    return {
        "service": "query-executor", 
        "version": "1.0.0",
        "status": "running",
        "max_query_timeout": settings.query_timeout
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    )