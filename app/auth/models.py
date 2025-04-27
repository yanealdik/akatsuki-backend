from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import string

from app.database import Base

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    xp = Column(Integer, default=0)
    is_active = Column(Boolean, default=False)  # Изменено на False по умолчанию
    is_verified = Column(Boolean, default=False)  # Новое поле для верификации email
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
        
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)
    code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)

    @staticmethod
    def generate_code(length=6):
        """Генерирует случайный код указанной длины"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def is_expired(expires_at):
        """Проверяет, истёк ли срок действия кода"""
        return datetime.now() > expires_at