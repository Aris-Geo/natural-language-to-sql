import time
import logging
from typing import Dict, Any, List, Optional

from service.http_client import ServiceHTTPClient
from schemas import TextToSQLRequest, TextToSQLResponse, ServiceTiming, DebugInfo
from config import settings

# Flow:
# 1. Get database schema (schema_validator)
# 2. Generate SQL from text (query_generator)
# 3. Execute SQL safely (query_executor)
# 4. Return formatted results

logger = logging.getLogger(__name__)

class TextToSQLOrchestrator:
    
    def __init__(self):
        self.http_client = ServiceHTTPClient()
        self.cache = {}
    
    async def process_query(self, request: TextToSQLRequest) -> TextToSQLResponse:
        start_time = time.time()
        timing = ServiceTiming()
        debug_info = DebugInfo(
            generated_sql="",
            schema_tables_count=0,
            services_called=[]
        )
        service_errors = {}
        
        try:
            logger.info(f"Starting schema introspection for database: {request.database.database}")
            schema_start = time.time()
            
            try:
                schema_response = await self.http_client.call_schema_validator(
                    request.database.dict()
                )
                timing.schema_validation_time = time.time() - schema_start
                debug_info.services_called.append("schema_validator")
                
                if not schema_response.get("success"):
                    raise Exception(f"Schema validation failed: {schema_response.get('error', 'Unknown error')}")
                
                schema_data = schema_response["schema"]
                debug_info.schema_tables_count = schema_data.get("total_tables", 0)
                logger.info(f"Schema introspection successful: {debug_info.schema_tables_count} tables found")
                
            except Exception as e:
                service_errors["schema_validator"] = str(e)
                logger.error(f"Schema validation failed: {str(e)}")
                return TextToSQLResponse(
                    success=False,
                    question=request.question,
                    error=f"Schema validation failed: {str(e)}",
                    service_errors=service_errors,
                    timing=timing
                )
            
            logger.info(f"Generating SQL for question: '{request.question}'")
            generation_start = time.time()
            
            try:
                generation_response = await self.http_client.call_query_generator(
                    request.question,
                    schema_data,
                    request.include_explanation
                )
                timing.sql_generation_time = time.time() - generation_start
                debug_info.services_called.append("query_generator")
                
                if not generation_response.get("success"):
                    raise Exception(f"SQL generation failed: {generation_response.get('error', 'Unknown error')}")
                
                generated_sql = generation_response["sql_query"]
                explanation = generation_response.get("explanation")
                debug_info.generated_sql = generated_sql
                debug_info.model_used = generation_response.get("model_used", "unknown")
                logger.info(f"SQL generation successful: {generated_sql}")
                
            except Exception as e:
                service_errors["query_generator"] = str(e)
                logger.error(f"SQL generation failed: {str(e)}")
                return TextToSQLResponse(
                    success=False,
                    question=request.question,
                    error=f"SQL generation failed: {str(e)}",
                    service_errors=service_errors,
                    timing=timing,
                    database_name=schema_data.get("database_name"),
                    debug_info=debug_info if settings.include_debug_info else None
                )
            
            logger.info(f"Executing SQL query: {generated_sql}")
            execution_start = time.time()
            
            try:
                execution_response = await self.http_client.call_query_executor(
                    generated_sql,
                    request.database.dict(),
                    request.limit_rows
                )
                timing.query_execution_time = time.time() - execution_start
                debug_info.services_called.append("query_executor")
                
                if not execution_response.get("success"):
                    error_msg = execution_response.get("error", "Unknown execution error")
                    validation_errors = execution_response.get("validation_errors", [])
                    if validation_errors:
                        error_msg += f". Validation issues: {', '.join(validation_errors)}"
                    raise Exception(error_msg)
                
                data = execution_response.get("data", [])
                metadata = execution_response.get("metadata", {})
                debug_info.validation_warnings = execution_response.get("validation_errors", [])
                
                logger.info(f"Query execution successful: {len(data)} rows returned")
                
            except Exception as e:
                service_errors["query_executor"] = str(e)
                logger.error(f"Query execution failed: {str(e)}")
                return TextToSQLResponse(
                    success=False,
                    question=request.question,
                    generated_sql=generated_sql,
                    explanation=explanation,
                    error=f"Query execution failed: {str(e)}",
                    service_errors=service_errors,
                    timing=timing,
                    database_name=schema_data.get("database_name"),
                    debug_info=debug_info if settings.include_debug_info else None
                )
            
            timing.total_time = time.time() - start_time
            
            response = TextToSQLResponse(
                success=True,
                data=data,
                question=request.question,
                generated_sql=generated_sql,
                explanation=explanation,
                rows_returned=len(data),
                columns_returned=len(metadata.get("column_names", [])),
                column_names=metadata.get("column_names", []),
                database_name=schema_data.get("database_name"),
                timing=timing if settings.include_timing_info else None,
                debug_info=debug_info if settings.include_debug_info else None,
                schema_info=schema_data if request.include_schema_info else None
            )
            
            logger.info(f"Text-to-SQL processing completed successfully in {timing.total_time:.2f}s")
            return response
            
        except Exception as e:
            timing.total_time = time.time() - start_time
            logger.error(f"Unexpected error in text-to-SQL processing: {str(e)}")
            
            return TextToSQLResponse(
                success=False,
                question=request.question,
                error=f"Unexpected error: {str(e)}",
                service_errors=service_errors,
                timing=timing if settings.include_timing_info else None,
                debug_info=debug_info if settings.include_debug_info else None
            )
    
    async def get_services_health(self) -> Dict[str, str]:
        return await self.http_client.check_all_services_health()
    
    async def test_database_connection(self, database_config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self.http_client.call_schema_validator(database_config)
            return {
                "success": response.get("success", False),
                "message": "Database connection successful" if response.get("success") else "Connection failed",
                "details": response
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Database connection failed: {str(e)}",
                "details": None
            }