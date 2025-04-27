import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Настройки приложения
    APP_NAME: str = "Akatsuki Backend"
    DEBUG: bool = True  # В продакшне установить False
    
    # Настройки базы данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:aldik07bak@localhost:5432/akatsuki")
    
    # Настройки JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа
    
    # Настройки CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5173/akatsuki.github.io"]
    
    # Настройки Email
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@akatsuki.com")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Akatsuki Education")
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    class Config:
        case_sensitive = True

settings = Settings()