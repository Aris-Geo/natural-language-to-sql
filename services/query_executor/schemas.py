from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
from datetime import datetime

class DatabaseConnection(BaseModel):
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    
    def get_connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class ExecuteQueryRequest(BaseModel):
    sql_query: str = Field(..., min_length=1, description="SQL query to execute")
    database: DatabaseConnection = Field(..., description="Database connection info")
    limit_rows: Optional[int] = Field(None, ge=1, le=10000, description="Maximum rows to return")
    
    @validator('sql_query')
    def validate_sql_query(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('SQL query cannot be empty')
        
        if not v.endswith(';'):
            v += ';'
        
        return v

class QueryMetadata(BaseModel):
    query_executed: str
    execution_time: float
    rows_returned: int
    columns_returned: int
    column_names: List[str]
    database_name: str
    executed_at: datetime

class ExecuteQueryResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]] = []
    metadata: Optional[QueryMetadata] = None
    error: Optional[str] = None
    validation_errors: List[str] = []

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    sanitized_query: Optional[str] = None