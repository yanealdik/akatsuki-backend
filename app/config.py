import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Настройки приложения
    APP_NAME: str = "Akatsuki Backend"
    
    # Настройки базы данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/akatsuki")
    
    # Настройки JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа
    
    # Настройки CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        case_sensitive = True

settings = Settings()