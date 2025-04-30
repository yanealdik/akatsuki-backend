from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.auth.router import router as auth_router
from app.courses.router import router as courses_router
from app.users.router import router as users_router
from app.config import settings
from app.database import engine, Base

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API для образовательной платформы Akatsuki",
    version="0.1.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(users_router)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Akatsuki!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

#uvicorn app.main:app --reload

