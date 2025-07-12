from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class DatabaseSchema(BaseModel):
    database_name: str
    tables: Dict[str, Any]
    total_tables: int
    total_columns: int
    relationships: List[Dict[str, str]]

class GenerateQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="Natural language question")
    schema: DatabaseSchema = Field(..., description="Database schema context")
    include_explanation: bool = Field(False, description="Include explanation of the generated SQL")

class GenerateQueryResponse(BaseModel):
    success: bool
    sql_query: Optional[str] = None
    explanation: Optional[str] = None
    error: Optional[str] = None
    model_used: str
    generation_time: float

class ModelStatusResponse(BaseModel):
    model_available: bool
    model_name: str
    ollama_status: str
    error: Optional[str] = None