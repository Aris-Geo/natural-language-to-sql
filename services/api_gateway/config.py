from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    
    schema_validator_url: str = "http://schema-validator:8000"
    query_generator_url: str = "http://query-generator:8000"
    query_executor_url: str = "http://query-executor:8000"
    
    service_timeout: int = 60
    schema_timeout: int = 30
    generation_timeout: int = 45
    execution_timeout: int = 30
    
    max_question_length: int = 500
    max_concurrent_requests: int = 10
    
    enable_caching: bool = False
    cache_ttl: int = 300
    
    include_debug_info: bool = True
    include_timing_info: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()