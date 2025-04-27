from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.auth.models import User
from app.auth.schemas import UserCreate, UserResponse, Token
from app.auth.jwt import create_access_token, get_current_user
from app.config import settings
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
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
    
    # Создаем нового пользователя
    hashed_password = User.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        nickname=user_data.nickname,
        password_hash=hashed_password,
        xp=0
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    # Находим пользователя по email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Проверяем пароль
    if not user or not User.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
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