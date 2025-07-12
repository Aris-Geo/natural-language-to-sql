from fastapi import APIRouter, HTTPException
from service.query_executor import QueryExecutorService
from schemas import ExecuteQueryRequest, ExecuteQueryResponse, ValidationResult
from config import settings

router = APIRouter()
executor_service = QueryExecutorService()

@router.post("/query", response_model=ExecuteQueryResponse)
async def execute_sql_query(request: ExecuteQueryRequest):
    try:
        limit_rows = request.limit_rows or settings.max_rows
        
        result = await executor_service.execute_query(
            request.sql_query,
            request.database,
            limit_rows
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )

@router.post("/validate")
async def validate_sql_query(request: ExecuteQueryRequest):
    try:
        validation_result = executor_service.validator.validate_query(request.sql_query)
        
        return {
            "is_valid": validation_result.is_valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "sanitized_query": validation_result.sanitized_query
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query validation failed: {str(e)}"
        )

@router.post("/test-connection")
async def test_database_connection(request: ExecuteQueryRequest):
    try:
        is_connected = await executor_service.test_connection(request.database)
        
        return {
            "success": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed",
            "database": request.database.database,
            "host": request.database.host
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Connection test failed: {str(e)}"
        )

@router.post("/explain")
async def explain_query(request: ExecuteQueryRequest):
    try:
        plan = await executor_service.get_query_plan(request.sql_query, request.database)
        
        return {
            "success": "error" not in plan,
            "execution_plan": plan,
            "query": request.sql_query
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query plan generation failed: {str(e)}"
        )

@router.post("/test")
async def test_execution():
    from schemas import DatabaseConnection
    
    test_query = "SELECT 1 as test_column, 'Hello World' as message;"
    
    return {
        "success": True,
        "message": "Test endpoint working",
        "example_query": test_query,
        "note": "Provide actual database credentials to test execution"
    }