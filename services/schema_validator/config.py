from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    max_connections: int = 5
    connection_timeout: int = 30
    max_sample_rows: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()