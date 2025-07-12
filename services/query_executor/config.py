from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    
    query_timeout: int = 30  # seconds timeout threshold
    max_rows: int = 1000     
    max_connections: int = 10
    connection_timeout: int = 30
    
    # in order to prevent breaking actions, we configure a list of allowed and blocked query actions.
    # SELECT and WITH (CTEs) are only allowed, actions such as alter/drop/delete/update are blocked in order to keep data integrity
    allowed_sql_keywords: list = ["SELECT", "WITH"]
    blocked_sql_keywords: list = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", 
        "TRUNCATE", "GRANT", "REVOKE", "EXECUTE", "CALL"
    ]
    
    max_column_width: int = 1000
    include_metadata: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()