import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.auth.models import User, VerificationCode
from app.config import settings

logger = logging.getLogger(__name__)

def create_verification_code(db: Session, user_id: int, email: str) -> VerificationCode:
    """
    Создает новый код верификации и сохраняет его в базе данных.
    """
    # Генерируем новый код
    code = VerificationCode.generate_code()
    
    # Устанавливаем срок действия (30 минут)
    expires_at = datetime.now() + timedelta(minutes=30)
    
    # Создаем запись в базе данных
    db_code = VerificationCode(
        user_id=user_id,
        email=email,
        code=code,
        expires_at=expires_at
    )
    
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    
    return db_code

def verify_code(db: Session, email: str, code: str) -> Optional[User]:
    """
    Проверяет код верификации. Возвращает пользователя, если код верный.
    """
    # Находим последний активный код для email
    db_code = (
        db.query(VerificationCode)
        .filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.is_used == False
        )
        .order_by(VerificationCode.created_at.desc())
        .first()
    )
    
    if not db_code:
        return None
    
    # Проверяем, не истек ли срок действия
    if VerificationCode.is_expired(db_code.expires_at):
        return None
    
    # Отмечаем код как использованный
    db_code.is_used = True
    db.add(db_code)
    
    # Активируем пользователя
    user = db.query(User).filter(User.id == db_code.user_id).first()
    if user:
        user.is_verified = True
        user.is_active = True
        db.add(user)
    
    db.commit()
    
    return user

def send_verification_email(email: str, code: str) -> bool:
    """
    Отправляет email с кодом верификации.
    Это заглушка - в реальном приложении здесь будет отправка через SMTP.
    """
    # В режиме разработки просто логируем код
    logger.info(f"Verification code for {email}: {code}")
    
    # Здесь должен быть код для отправки email
    # Например, с использованием библиотеки smtplib или FastAPI-Mail
    
    # Для тестирования считаем, что email отправлен успешно
    return True

def send_welcome_email(email: str) -> bool:
    """
    Отправляет приветственное письмо после успешной верификации.
    Это заглушка - в реальном приложении здесь будет отправка через SMTP.
    """
    # В режиме разработки просто логируем
    logger.info(f"Welcome email sent to {email}")
    
    # Здесь должен быть код для отправки приветственного email
    
    # Для тестирования считаем, что email отправлен успешно
    return True