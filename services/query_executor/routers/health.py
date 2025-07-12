from fastapi import APIRouter
from service.query_executor import QueryExecutorService

router = APIRouter()
executor_service = QueryExecutorService()

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "query-executor"}

@router.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "query-executor"}