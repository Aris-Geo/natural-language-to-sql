from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import query, health
from config import settings

app = FastAPI(
    title="Text-to-SQL API Gateway",
    description="Natural language to SQL query service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(query.router, prefix="/api", tags=["text-to-sql"])

@app.get("/")
async def root():
    return {
        "service": "text-to-sql-api-gateway", 
        "version": "1.0.0",
        "status": "running",
        "description": "Convert natural language questions to SQL and execute them",
        "endpoints": {
            "main": "query",
            "docs": "/docs",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    )