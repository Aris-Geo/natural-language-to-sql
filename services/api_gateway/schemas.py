from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
from datetime import datetime

class DatabaseConnection(BaseModel):
    host: str = Field(..., description="Database host")
    port: int = Field(5432, ge=1, le=65535, description="Database port")
    database: str = Field(..., min_length=1, description="Database name")
    username: str = Field(..., min_length=1, description="Database username")
    password: str = Field(..., min_length=1, description="Database password")

class TextToSQLRequest(BaseModel):
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=500, 
        description="Natural language question about the data"
    )
    database: DatabaseConnection = Field(..., description="Database connection details")
    include_explanation: bool = Field(False, description="Include explanation of generated SQL")
    limit_rows: Optional[int] = Field(None, ge=1, le=1000, description="Maximum rows to return")
    include_schema_info: bool = Field(False, description="Include database schema in response")
    
    @validator('question')
    def validate_question(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Question cannot be empty')
        return v

class ServiceTiming(BaseModel):
    schema_validation_time: float = 0.0
    sql_generation_time: float = 0.0
    query_execution_time: float = 0.0
    total_time: float = 0.0

class DebugInfo(BaseModel):
    generated_sql: str
    schema_tables_count: int
    validation_warnings: List[str] = []
    model_used: str = "unknown"
    services_called: List[str] = []

class TextToSQLResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]] = []
    
    question: str
    generated_sql: Optional[str] = None
    explanation: Optional[str] = None
    
    rows_returned: int = 0
    columns_returned: int = 0
    column_names: List[str] = []
    
    timing: Optional[ServiceTiming] = None
    debug_info: Optional[DebugInfo] = None
    
    database_name: Optional[str] = None
    schema_info: Optional[Dict[str, Any]] = None
    
    error: Optional[str] = None
    service_errors: Dict[str, str] = {}
    
    processed_at: datetime = Field(default_factory=datetime.now)

class ServiceHealthResponse(BaseModel):
    api_gateway: str = "healthy"
    schema_validator: str
    query_generator: str  
    query_executor: str
    overall_status: str
    checked_at: datetime = Field(default_factory=datetime.now)