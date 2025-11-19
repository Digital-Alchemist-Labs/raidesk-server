"""
Configuration management for RAiDesk backend
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss"
    
    # CORS - Support both development and production origins
    cors_origins: Union[List[str], str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Storage Configuration
    storage_type: str = "sqlite"  # "sqlite" or "redis"
    database_path: str = "./raidesk.db"  # For SQLite
    redis_url: str = "redis://localhost:6379"  # For Redis
    
    # Session & Plan TTL (in seconds)
    session_ttl: int = 86400  # 24 hours
    plan_ttl: int = 604800  # 7 days (or None for no expiration)
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # LangSmith (Optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "raidesk"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split comma-separated string into list
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

