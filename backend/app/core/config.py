from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Strategic Analytics Dashboard"
    VERSION: str = "1.0.0"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    CONFIG_BUCKET: str = "satcom-config"
    DATA_BUCKET: str = "satcom-data"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # Add more as needed
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 