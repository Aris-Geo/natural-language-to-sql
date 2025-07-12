from fastapi import APIRouter, HTTPException, BackgroundTasks
from service.orchestrator import TextToSQLOrchestrator
from schemas import TextToSQLRequest, TextToSQLResponse
import logging

router = APIRouter()
orchestrator = TextToSQLOrchestrator()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=TextToSQLResponse)
async def text_to_sql_query(request: TextToSQLRequest):
    try:
        logger.info(f"Processing text-to-SQL request: '{request.question}' for database: {request.database.database}")
        
        result = await orchestrator.process_query(request)
        
        if not result.success:
            # return the error response (don't raise HTTPException)
            # this allows the user to see detailed error information
            return result
        
        logger.info(f"Text-to-SQL request completed successfully: {result.rows_returned} rows returned")
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in text-to-SQL endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/test-connection")
async def test_database_connection(request: TextToSQLRequest):
    try:
        result = await orchestrator.test_database_connection(request.database.dict())
        
        return {
            "success": result["success"],
            "message": result["message"],
            "database": request.database.database,
            "host": request.database.host,
            "details": result.get("details")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )

@router.post("/explain")
async def explain_query_flow(request: TextToSQLRequest):
    try:
        return {
            "flow": [
                {
                    "step": 1,
                    "service": "schema_validator",
                    "action": f"Introspect database '{request.database.database}' to get table structures and relationships"
                },
                {
                    "step": 2,
                    "service": "query_generator", 
                    "action": f"Convert question '{request.question}' to SQL using database schema context"
                },
                {
                    "step": 3,
                    "service": "query_executor",
                    "action": "Validate and execute the generated SQL safely, returning JSON results"
                }
            ],
            "question": request.question,
            "database": request.database.database,
            "options": {
                "include_explanation": request.include_explanation,
                "limit_rows": request.limit_rows,
                "include_schema_info": request.include_schema_info
            },
            "note": "This is an explanation of the process. Use /query to actually execute it."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain query flow: {str(e)}"
        )

@router.get("/example")
async def get_example_request():
    return {
        "example_request": {
            "question": "Show me the top 5 customers by total spending",
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "ecommerce_demo",
                "username": "demo_user",
                "password": "demo_pass"
            },
            "include_explanation": True,
            "limit_rows": 10,
            "include_schema_info": False
        },
        "example_curl": """
curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "Show me the top 5 customers by total spending",
    "database": {
      "host": "localhost",
      "port": 5432,
      "database": "ecommerce_demo", 
      "username": "demo_user",
      "password": "demo_pass"
    },
    "include_explanation": true
  }'
        """.strip()
    }