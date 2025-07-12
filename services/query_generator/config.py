from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    
    # configure the llm
    ollama_host: str = "ollama"
    ollama_port: int = 11434
    ollama_model: str = "codellama:7b"  # most lightweight model
    
    max_tokens: int = 200
    temperature: float = 0.1
    timeout: int = 30
    
    max_context_length: int = 4000
    include_sample_data: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()