from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.auth.models import User, VerificationCode
from app.auth.schemas import UserCreate, UserResponse, Token, VerificationRequest, VerificationSubmit, VerificationResponse
from app.auth.jwt import create_access_token, get_current_user
from app.config import settings
from app.database import get_db
from app.utils.email import create_verification_code, verify_code, send_verification_email, send_welcome_email

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> Any:
    # Проверяем, что email не занят
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован",
        )
    
    # Проверяем, что никнейм не занят
    db_nickname = db.query(User).filter(User.nickname == user_data.nickname).first()
    if db_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Никнейм уже занят",
        )
    
    # Создаем нового пользователя (неактивного до верификации)
    hashed_password = User.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        nickname=user_data.nickname,
        password_hash=hashed_password,
        xp=0,
        is_active=False,
        is_verified=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаем и отправляем код верификации
    verification = create_verification_code(db, db_user.id, db_user.email)
    background_tasks.add_task(send_verification_email, db_user.email, verification.code)
    
    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    # Находим пользователя по email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Проверяем пароль и статус аккаунта
    if not user or not User.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, что аккаунт активен и верифицирован
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не активирован. Пожалуйста, подтвердите email.",
        )
    
    # Создаем access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)) -> Any:
    return current_user

@router.post("/verification/send", response_model=VerificationResponse)
def send_verification_code(
    data: VerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    # Находим пользователя по email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден",
        )
    
    # Создаем новый код верификации
    verification = create_verification_code(db, user.id, user.email)
    
    # Отправляем код верификации (асинхронно)
    background_tasks.add_task(send_verification_email, user.email, verification.code)
    
    # В режиме разработки возвращаем код в ответе (убрать в продакшне)
    return {
        "message": "Код верификации отправлен на указанный email",
        "code": verification.code if settings.DEBUG else None
    }

@router.post("/verification/verify", response_model=VerificationResponse)
def verify_email(
    data: VerificationSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    # Проверяем код верификации
    user = verify_code(db, data.email, data.code)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код верификации или срок его действия истек",
        )
    
    # Отправляем приветственное сообщение
    background_tasks.add_task(send_welcome_email, user.email)
    
    return {
        "message": "Email успешно подтвержден. Теперь вы можете войти в аккаунт."
    }