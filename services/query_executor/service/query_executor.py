# services/query_executor/service/query_executor.py
import asyncio
import asyncpg
import time
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from service.sql_validator import SQLValidator
from schemas import DatabaseConnection, QueryMetadata, ExecuteQueryResponse, ValidationResult
from config import settings

logger = logging.getLogger(__name__)

class QueryExecutorService:
    
    def __init__(self):
        self.validator = SQLValidator()
        self.connection_pools = {}
    
    async def execute_query(self, sql_query: str, db_config: DatabaseConnection, limit_rows: int = None) -> ExecuteQueryResponse:

        start_time = time.time()
        
        try:
            validation_result = self.validator.validate_query(sql_query)
            
            if not validation_result.is_valid:
                return ExecuteQueryResponse(
                    success=False,
                    validation_errors=validation_result.errors,
                    error="Query validation failed"
                )
            
            sanitized_query = validation_result.sanitized_query
            
            if limit_rows:
                sanitized_query = self._apply_row_limit(sanitized_query, limit_rows)
            
            results, column_names = await self._execute_safe_query(sanitized_query, db_config)
            
            formatted_results = self._format_results(results, column_names)
            
            execution_time = time.time() - start_time
            
            metadata = QueryMetadata(
                query_executed=sanitized_query,
                execution_time=execution_time,
                rows_returned=len(formatted_results),
                columns_returned=len(column_names),
                column_names=column_names,
                database_name=db_config.database,
                executed_at=datetime.now()
            )
            
            return ExecuteQueryResponse(
                success=True,
                data=formatted_results,
                metadata=metadata,
                validation_errors=validation_result.warnings
            )
            
        except asyncio.TimeoutError:
            return ExecuteQueryResponse(
                success=False,
                error=f"Query execution timed out after {settings.query_timeout} seconds"
            )
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return ExecuteQueryResponse(
                success=False,
                error=f"Query execution failed: {str(e)}"
            )
    
    async def _execute_safe_query(self, sql_query: str, db_config: DatabaseConnection) -> Tuple[List[Any], List[str]]:
        connection_string = db_config.get_connection_string()
        
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(connection_string),
                timeout=settings.connection_timeout
            )
            
            try:
                result = await asyncio.wait_for(
                    conn.fetch(sql_query),
                    timeout=settings.query_timeout
                )
                
                if result:
                    column_names = list(result[0].keys())
                    rows = [tuple(record.values()) for record in result]
                else:
                    column_names = []
                    rows = []
                
                return rows, column_names
                
            finally:
                await conn.close()
                
        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL error: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise
    
    def _apply_row_limit(self, sql_query: str, limit_rows: int) -> str:
        query_upper = sql_query.upper()
        
        if 'LIMIT' in query_upper:
            import re
            pattern = r'\bLIMIT\s+\d+\b'
            sql_query = re.sub(pattern, f'LIMIT {limit_rows}', sql_query, flags=re.IGNORECASE)
        else:
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1] + f' LIMIT {limit_rows};'
            else:
                sql_query += f' LIMIT {limit_rows}'
        
        return sql_query
    
    def _format_results(self, rows: List[Any], column_names: List[str]) -> List[Dict[str, Any]]:
        formatted_results = []
        
        for row in rows:
            row_dict = {}
            for i, column_name in enumerate(column_names):
                value = row[i] if i < len(row) else None
                row_dict[column_name] = self._serialize_value(value)
            formatted_results.append(row_dict)
        
        if len(formatted_results) > settings.max_rows:
            formatted_results = formatted_results[:settings.max_rows]
        
        return formatted_results
    
    def _serialize_value(self, value: Any) -> Any:
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            if isinstance(value, str) and len(value) > settings.max_column_width:
                return value[:settings.max_column_width] + "..."
            return value
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, UUID):
            return str(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        else:
            return str(value)
    
    async def test_connection(self, db_config: DatabaseConnection) -> bool:
        try:
            connection_string = db_config.get_connection_string()
            conn = await asyncio.wait_for(
                asyncpg.connect(connection_string),
                timeout=settings.connection_timeout
            )
            await conn.close()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def get_query_plan(self, sql_query: str, db_config: DatabaseConnection) -> Dict[str, Any]:
        try:
            validation_result = self.validator.validate_query(sql_query)
            if not validation_result.is_valid:
                return {"error": "Query validation failed", "errors": validation_result.errors}
            
            explain_query = f"EXPLAIN (FORMAT JSON) {validation_result.sanitized_query}"
            
            connection_string = db_config.get_connection_string()
            conn = await asyncpg.connect(connection_string)
            
            try:
                result = await conn.fetchval(explain_query)
                return {"plan": result[0] if result else None}
            finally:
                await conn.close()
                
        except Exception as e:
            return {"error": str(e)}