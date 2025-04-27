import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.auth.models import User
from app.courses.models import Course, UserCourse, CourseStatus

# Пересоздаем все таблицы
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        # Создаем тестовых пользователей
        test_users = [
            {
                "email": "user1@example.com",
                "nickname": "ninja1",
                "password": "testpassword1"
            },
            {
                "email": "user2@example.com",
                "nickname": "ninja2",
                "password": "testpassword2"
            },
            {
                "email": "admin@akatsuki.com",
                "nickname": "admin",
                "password": "adminpassword"
            }
        ]
        
        users = []
        for user_data in test_users:
            hashed_password = User.get_password_hash(user_data["password"])
            user = User(
                email=user_data["email"],
                nickname=user_data["nickname"],
                password_hash=hashed_password,
                xp=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            users.append(user)
        
        # Создаем тестовые курсы
        test_courses = [
            {
                "title": "Введение в Python",
                "description": "Базовый курс по языку программирования Python",
                "duration": 120,  # минут
                "xp_reward": 100
            },
            {
                "title": "FastAPI для начинающих",
                "description": "Создание API с использованием FastAPI",
                "duration": 180,
                "xp_reward": 150
            },
            {
                "title": "Основы React",
                "description": "Основы разработки интерфейсов с использованием React",
                "duration": 240,
                "xp_reward": 200
            },
            {
                "title": "Продвинутый JavaScript",
                "description": "Углубленный курс по JavaScript",
                "duration": 300,
                "xp_reward": 250
            },
            {
                "title": "Базы данных: PostgreSQL",
                "description": "Работа с PostgreSQL для веб-разработчиков",
                "duration": 210,
                "xp_reward": 180
            }
        ]
        
        courses = []
        for course_data in test_courses:
            course = Course(**course_data)
            db.add(course)
            db.commit()
            db.refresh(course)
            courses.append(course)
        
        # Записываем пользователей на курсы
        # Пользователь 1 завершил первый курс
        user_course1 = UserCourse(
            user_id=users[0].id,
            course_id=courses[0].id,
            status=CourseStatus.COMPLETED,
            progress=100,
            earned_xp=courses[0].xp_reward
        )
        db.add(user_course1)
        
        # Пользователь 1 изучает второй курс
        user_course2 = UserCourse(
            user_id=users[0].id,
            course_id=courses[1].id,
            status=CourseStatus.IN_PROGRESS,
            progress=50,
            earned_xp=0
        )
        db.add(user_course2)
        
        # Пользователь 2 изучает первый и третий курсы
        user_course3 = UserCourse(
            user_id=users[1].id,
            course_id=courses[0].id,
            status=CourseStatus.IN_PROGRESS,
            progress=75,
            earned_xp=0
        )
        db.add(user_course3)
        
        user_course4 = UserCourse(
            user_id=users[1].id,
            course_id=courses[2].id,
            status=CourseStatus.IN_PROGRESS,
            progress=30,
            earned_xp=0
        )
        db.add(user_course4)
        
        # Обновляем XP пользователей
        users[0].xp = courses[0].xp_reward  # XP за завершенный курс
        db.add(users[0])
        
        db.commit()
        
        print("База данных успешно заполнена тестовыми данными!")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при заполнении базы данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()