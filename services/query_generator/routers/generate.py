from fastapi import APIRouter, HTTPException
from service.text_to_sql import TextToSQLService
from schemas import GenerateQueryRequest, GenerateQueryResponse
from config import settings

router = APIRouter()
text_to_sql_service = TextToSQLService()

@router.post("/sql", response_model=GenerateQueryResponse)
async def generate_sql_query(request: GenerateQueryRequest):
    try:
        sql_query, explanation, generation_time = await text_to_sql_service.generate_sql(
            request.question,
            request.schema,
            request.include_explanation
        )
        
        if not sql_query:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate valid SQL query"
            )
        
        return GenerateQueryResponse(
            success=True,
            sql_query=sql_query,
            explanation=explanation,
            model_used=settings.ollama_model,
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL generation failed: {str(e)}"
        )

@router.post("/test")
async def test_generation():
    from schemas import DatabaseSchema
    
    test_schema = DatabaseSchema(
        database_name="test_db",
        tables={
            "users": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR", "primary_key": False},
                    {"name": "email", "type": "VARCHAR", "primary_key": False}
                ],
                "foreign_keys": [],
                "sample_data": [{"id": 1, "name": "Aris", "email": "aris@test.com"}]
            }
        },
        total_tables=1,
        total_columns=3,
        relationships=[]
    )
    
    try:
        sql_query, explanation, generation_time = await text_to_sql_service.generate_sql(
            "Show me all users",
            test_schema,
            True
        )
        
        return {
            "success": True,
            "test_question": "Show me all users",
            "generated_sql": sql_query,
            "explanation": explanation,
            "generation_time": generation_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test generation failed: {str(e)}"
        )