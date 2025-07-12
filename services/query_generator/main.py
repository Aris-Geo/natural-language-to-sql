from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import generate, health
from config import settings

app = FastAPI(
    title="Query Generator",
    description="Natural language to SQL query generation service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #tbd based on deployed envs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(generate.router, prefix="generate", tags=["generation"])

@app.get("/")
async def root():
    return {
        "service": "query-generator", 
        "version": "1.0.0",
        "status": "running",
        "model": settings.ollama_model
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug
    )