import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.auth.models import User, VerificationCode
from app.config import settings


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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

def send_email(to_email: str, subject: str, content: str) -> bool:
    """
    Generic function to send emails using the application settings.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Email content (HTML)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        # Attach content
        message.attach(MIMEText(content, "html"))
        
        # Connect to SMTP server
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            # Start TLS if enabled
            if settings.MAIL_TLS:
                server.starttls()
            
            # Login if credentials provided
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
            # Send email
            server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_verification_email(email: str, code: str) -> bool:
    """
    Отправляет email с кодом верификации.
    """
    subject = "Ваш код подтверждения - Akatsuki Education"
    content = f"""
    <html>
        <body>
            <h1>Подтверждение регистрации</h1>
            <p>Здравствуйте!</p>
            <p>Ваш код подтверждения: <strong>{code}</strong></p>
            <p>Введите этот код на странице регистрации, чтобы завершить процесс.</p>
            <p>С уважением,<br>Команда Akatsuki Education</p>
        </body>
    </html>
    """
    
    # В режиме разработки логируем код
    if settings.DEBUG:
        logger.info(f"Verification code for {email}: {code}")
    
    return send_email(email, subject, content)


def send_welcome_email(email: str) -> bool:
    """
    Отправляет приветственное письмо после успешной верификации.
    """
    subject = "Добро пожаловать в Akatsuki Education!"
    content = f"""
    <html>
        <body>
            <h1>Добро пожаловать!</h1>
            <p>Здравствуйте!</p>
            <p>Мы рады приветствовать вас на платформе Akatsuki Education.</p>
            <p>Ваш аккаунт успешно активирован, и теперь вы можете использовать все возможности нашей платформы.</p>
            <p>С уважением,<br>Команда Akatsuki Education</p>
        </body>
    </html>
    """
    
    # В режиме разработки логируем
    if settings.DEBUG:
        logger.info(f"Welcome email sent to {email}")
    
    return send_email(email, subject, content)