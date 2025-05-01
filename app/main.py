from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.auth.router import router as auth_router
from app.courses.lessons_router import router as courses_router
from app.courses.lessons_router import router as lessons_router
from app.users.router import router as users_router

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI
app = FastAPI(
    title="Akatsuki Courses API",
    description="API для платформы обучения программированию",
    version="1.0.0"
)

# Добавляем CORS middleware для разрешения запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(lessons_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {
        "message": "Добро пожаловать в API Akatsuki Courses!",
        "docs": "/docs"
    }