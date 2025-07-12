from fastapi import APIRouter, HTTPException
from services.schema_validator import SchemaIntrospector
from schemas import SchemaRequest, SchemaResponse

router = APIRouter()
introspector = SchemaIntrospector()

# our main endpoint, responsible for performing a database retrospection
# retrieves schema information, keys, columns and table connections from our target db
@router.post("/introspect", response_model=SchemaResponse)
async def introspect_database(request: SchemaRequest):
    try:
        schema = await introspector.get_schema(
            request.database,
            request.include_sample_data,
            request.max_sample_rows
        )
        
        return SchemaResponse(
            success=True,
            schema=schema,
            connection_id=request.database.get_connection_id()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Schema introspection failed: {str(e)}"
        )

@router.post("/test-connection")
async def test_database_connection(request: SchemaRequest):
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(request.database.get_connection_string())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.scalar()
        
        engine.dispose()
        
        return {
            "success": True,
            "message": "Database connection successful",
            "connection_id": request.database.get_connection_id()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Database connection failed: {str(e)}"
        )