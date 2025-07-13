import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)

class ServiceHTTPClient:
    
    def __init__(self):
        self.timeout = httpx.Timeout(settings.service_timeout)
        self.services = {
            "schema_validator": settings.schema_validator_url,
            "query_generator": settings.query_generator_url,
            "query_executor": settings.query_executor_url
        }
    
    async def call_schema_validator(self, database_config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            url = f"{self.services['schema_validator']}/introspect"
            
            payload = {
                "database": database_config,
                "include_sample_data": True,
                "max_sample_rows": 3
            }
            
            async with httpx.AsyncClient(timeout=settings.schema_timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Schema validator request failed: {str(e)}")
            raise Exception(f"Failed to connect to schema validator: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Schema validator HTTP error: {e.response.status_code}")
            try:
                error_detail = e.response.json().get('detail', 'Unknown error')
            except:
                error_detail = e.response.text
            raise Exception(f"Schema validation failed: {error_detail}")
        except Exception as e:
            logger.error(f"Unexpected error in schema validation: {str(e)}")
            raise
    
    async def call_query_generator(self, question: str, schema_data: Dict[str, Any], include_explanation: bool = False) -> Dict[str, Any]:
        try:
            url = f"{self.services['query_generator']}/sql"
            
            payload = {
                "question": question,
                "schema": schema_data,
                "include_explanation": include_explanation
            }
            
            async with httpx.AsyncClient(timeout=settings.generation_timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Query generator request failed: {str(e)}")
            raise Exception(f"Failed to connect to query generator: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Query generator HTTP error: {e.response.status_code}")
            try:
                error_detail = e.response.json().get('detail', 'Unknown error')
            except:
                error_detail = e.response.text
            raise Exception(f"SQL generation failed: {error_detail}")
        except Exception as e:
            logger.error(f"Unexpected error in SQL generation: {str(e)}")
            raise
    
    async def call_query_executor(self, sql_query: str, database_config: Dict[str, Any], limit_rows: Optional[int] = None) -> Dict[str, Any]:
        try:
            url = f"{self.services['query_executor']}execute/query"
            
            payload = {
                "sql_query": sql_query,
                "database": database_config,
                "limit_rows": limit_rows
            }
            
            async with httpx.AsyncClient(timeout=settings.execution_timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Query executor request failed: {str(e)}")
            raise Exception(f"Failed to connect to query executor: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Query executor HTTP error: {e.response.status_code}")
            try:
                error_detail = e.response.json().get('detail', 'Unknown error')
            except:
                error_detail = e.response.text
            raise Exception(f"Query execution failed: {error_detail}")
        except Exception as e:
            logger.error(f"Unexpected error in query execution: {str(e)}")
            raise
    
    async def check_service_health(self, service_name: str) -> str:
        try:
            if service_name not in self.services:
                return "unknown"
            
            url = f"{self.services[service_name]}/health"
            
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                response.raise_for_status()
                return "healthy"
                
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {str(e)}")
            return "unhealthy"
    
    async def check_all_services_health(self) -> Dict[str, str]:
        health_checks = {}
        
        for service_name in self.services.keys():
            health_checks[service_name] = self.check_service_health(service_name)
        
        results = await asyncio.gather(*health_checks.values(), return_exceptions=True)
        
        service_health = {}
        for service_name, result in zip(health_checks.keys(), results):
            if isinstance(result, Exception):
                service_health[service_name] = "error"
            else:
                service_health[service_name] = result
        
        return service_health
    
    async def test_service_connectivity(self) -> Dict[str, bool]:
        connectivity = {}
        
        for service_name, base_url in self.services.items():
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{base_url}/health")
                    connectivity[service_name] = response.status_code == 200
            except Exception:
                connectivity[service_name] = False
        
        return connectivity