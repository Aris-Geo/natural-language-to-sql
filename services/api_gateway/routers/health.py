from fastapi import APIRouter
from service.orchestrator import TextToSQLOrchestrator
from schemas import ServiceHealthResponse

router = APIRouter()
orchestrator = TextToSQLOrchestrator()

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@router.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "api-gateway"}

@router.get("/services", response_model=ServiceHealthResponse)
async def check_all_services():
    services_health = await orchestrator.get_services_health()
    
    all_healthy = all(status == "healthy" for status in services_health.values())
    overall_status = "healthy" if all_healthy else "degraded"
    
    return ServiceHealthResponse(
        schema_validator=services_health.get("schema_validator", "unknown"),
        query_generator=services_health.get("query_generator", "unknown"),
        query_executor=services_health.get("query_executor", "unknown"),
        overall_status=overall_status
    )