from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class DatabaseConnection(BaseModel):
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    
    def get_connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_connection_id(self) -> str:
        return f"{self.host}:{self.port}/{self.database}"

class SchemaRequest(BaseModel):
    database: DatabaseConnection
    include_sample_data: bool = True
    max_sample_rows: int = Field(3, ge=1, le=10)

class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool = False
    default: Optional[str] = None

class ForeignKey(BaseModel):
    column: str
    references_table: str
    references_column: str

class TableInfo(BaseModel):
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKey]
    primary_keys: List[str]
    sample_data: List[Dict[str, Any]] = []
    row_count: Optional[int] = None

class DatabaseSchema(BaseModel):
    database_name: str
    tables: Dict[str, TableInfo]
    total_tables: int
    total_columns: int
    relationships: List[Dict[str, str]]

class SchemaResponse(BaseModel):
    success: bool
    schema: Optional[DatabaseSchema] = None
    error: Optional[str] = None
    connection_id: Optional[str] = None