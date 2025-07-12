from fastapi import APIRouter
from service.text_to_sql import TextToSQLService
from schemas import ModelStatusResponse

router = APIRouter()
text_to_sql_service = TextToSQLService()

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "query-generator"}

@router.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "query-generator"}

@router.get("/model-status", response_model=ModelStatusResponse)
async def check_model_status():
    status = await text_to_sql_service.check_service_health()
    
    return ModelStatusResponse(
        model_available=status.get("model_available", False),
        model_name=status.get("model_name", "unknown"),
        ollama_status=status.get("ollama_status", "unknown"),
        error=status.get("error")
    )
