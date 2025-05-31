from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Server Configuration
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_window: int = 60
    
    # File Management
    temp_dir: str = "temp"
    max_file_size_mb: int = 100
    cleanup_interval_hours: int = 1
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # FFmpeg Configuration
    ffmpeg_path: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.temp_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
