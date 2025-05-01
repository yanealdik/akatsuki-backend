"""
Скрипт для наполнения базы данных тестовыми данными.
"""
import os
import sys
from datetime import datetime, timedelta

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.auth.models import User
from app.courses.models import Course, UserCourse, CourseStatus
from app.courses.models import Module, Lesson, UserLessonProgress
from app.courses.models import TestQuestion, TestOption, LessonComment

def seed_database():
    db = next(get_db())
    
    try:
        print("Начало заполнения базы данных тестовыми данными...")
        
        # Создаем тестового пользователя, если его еще нет
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            print("Создание тестового пользователя...")
            hashed_password = User.get_password_hash("password123")
            test_user = User(
                email="test@example.com",
                nickname="Тестовый Пользователь",
                password_hash=hashed_password,
                xp=250,
                is_active=True,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Создан тестовый пользователь с ID: {test_user.id}")
        
        # Создаем тестовые курсы
        courses_data = [
            {
                "title": "Основы JavaScript",
                "description": "Базовый курс по JavaScript для начинающих. Вы научитесь основам языка, работе с переменными, функциями и объектами.",
                "duration": 180,
                "xp_reward": 500
            },
            {
                "title": "HTML и CSS для начинающих",
                "description": "Изучите основы веб-разработки с HTML и CSS. Создайте свой первый веб-сайт с нуля!",
                "duration": 150,
                "xp_reward": 450
            },
            {
                "title": "Python для анализа данных",
                "description": "Научитесь использовать Python для работы с данными, включая библиотеки Pandas и NumPy.",
                "duration": 210,
                "xp_reward": 600
            }
        ]
        
        created_courses = []
        for course_data in courses_data:
            existing_course = db.query(Course).filter(Course.title == course_data["title"]).first()
            if not existing_course:
                print(f"Создание курса: {course_data['title']}...")
                course = Course(**course_data)
                db.add(course)
                db.commit()
                db.refresh(course)
                created_courses.append(course)
                print(f"Создан курс с ID: {course.id}")
            else:
                created_courses.append(existing_course)
        
        # Записываем пользователя на курсы, если еще не записан
        for i, course in enumerate(created_courses):
            existing_enrollment = db.query(UserCourse).filter(
                UserCourse.user_id == test_user.id,
                UserCourse.course_id == course.id
            ).first()
            
            if not existing_enrollment:
                print(f"Запись пользователя на курс: {course.title}...")
                
                # Разные статусы для разных курсов
                if i == 0:  # Первый курс - завершен
                    status = CourseStatus.COMPLETED
                    progress = 100
                    earned_xp = course.xp_reward
                    completed_at = datetime.utcnow() - timedelta(days=7)
                elif i == 1:  # Второй курс - в процессе, 50% пройдено
                    status = CourseStatus.IN_PROGRESS
                    progress = 50
                    earned_xp = int(course.xp_reward * 0.5)
                    completed_at = None
                else:  # Остальные курсы - только начаты
                    status = CourseStatus.IN_PROGRESS
                    progress = 10
                    earned_xp = int(course.xp_reward * 0.1)
                    completed_at = None
                
                user_course = UserCourse(
                    user_id=test_user.id,
                    course_id=course.id,
                    status=status,
                    progress=progress,
                    earned_xp=earned_xp,
                    completed_at=completed_at
                )
                db.add(user_course)
                db.commit()
                db.refresh(user_course)
                print(f"Пользователь записан на курс. ID записи: {user_course.id}")
        
        # Добавляем модули и уроки для первого курса
        first_course = created_courses[0]
        
        # Проверяем, есть ли уже модули для курса
        existing_modules = db.query(Module).filter(Module.course_id == first_course.id).count()
        if existing_modules == 0:
            print(f"Создание модулей и уроков для курса: {first_course.title}...")
            
            # Модуль 1: Введение в JavaScript
            module1 = Module(
                course_id=first_course.id,
                title="Введение в JavaScript",
                description="Основы языка JavaScript и его роль в веб-разработке",
                order=1
            )
            db.add(module1)
            db.commit()
            db.refresh(module1)
            
            # Уроки для модуля 1
            lessons1 = [
                {
                    "title": "Что такое JavaScript",
                    "intro_title": "Знакомство с JavaScript",
                    "intro_content": "<p>JavaScript — это язык программирования, который используется для создания интерактивных веб-страниц.</p><p>В этом уроке вы узнаете о роли JavaScript в современной веб-разработке.</p>",
                    "video_url": "https://www.youtube.com/embed/ix9cRaBkVe0",
                    "video_description": "Обзор основ языка JavaScript и его применение в веб-разработке.",
                    "practice_instructions": "<p>Создайте свой первый скрипт с выводом сообщения в консоль.</p>",
                    "practice_code_template": "// Ваш первый JavaScript код\nconsole.log('Привет, мир!');\n\n// Попробуйте вывести еще одно сообщение\n",
                    "order": 1,
                    "xp_reward": 25
                },
                {
                    "title": "Основы синтаксиса",
                    "intro_title": "Синтаксис JavaScript",
                    "intro_content": "<p>Синтаксис JavaScript похож на C++ и Java.</p><p>В этом уроке мы рассмотрим основные элементы синтаксиса.</p>",
                    "video_url": "https://www.youtube.com/embed/ix9cRaBkVe0",
                    "video_description": "Подробный разбор синтаксиса JavaScript, включая переменные, операторы и выражения.",
                    "practice_instructions": "<p>Напишите код для объявления переменных разных типов.</p>",
                    "practice_code_template": "// Объявите переменные трех разных типов\nlet name = \"Имя\";\n\n// Создайте числовую переменную\n\n// Создайте булеву переменную\n",
                    "order": 2,
                    "xp_reward": 30
                }
            ]
            
            for lesson_data in lessons1:
                lesson = Lesson(module_id=module1.id, **lesson_data)
                db.add(lesson)
                db.commit()
                db.refresh(lesson)
                
                # Добавляем тестовые вопросы
                questions = [
                    {
                        "question": "Для чего используется JavaScript?",
                        "order": 1,
                        "options": [
                            {"text": "Только для серверной разработки", "is_correct": False, "order": 1},
                            {"text": "Для создания интерактивных веб-страниц", "is_correct": True, "order": 2},
                            {"text": "Только для мобильной разработки", "is_correct": False, "order": 3},
                            {"text": "Только для работы с базами данных", "is_correct": False, "order": 4}
                        ]
                    },
                    {
                        "question": "Какой тег используется для добавления JavaScript в HTML?",
                        "order": 2,
                        "options": [
                            {"text": "<javascript>", "is_correct": False, "order": 1},
                            {"text": "<script>", "is_correct": True, "order": 2},
                            {"text": "<js>", "is_correct": False, "order": 3},
                            {"text": "<code>", "is_correct": False, "order": 4}
                        ]
                    },
                    {
                        "question": "Какое ключевое слово используется для объявления переменной в современном JavaScript?",
                        "order": 3,
                        "options": [
                            {"text": "var", "is_correct": False, "order": 1},
                            {"text": "variable", "is_correct": False, "order": 2},
                            {"text": "let", "is_correct": True, "order": 3},
                            {"text": "string", "is_correct": False, "order": 4}
                        ]
                    }
                ]
                
                for q_data in questions:
                    options_data = q_data.pop("options")
                    question = TestQuestion(lesson_id=lesson.id, **q_data)
                    db.add(question)
                    db.commit()
                    db.refresh(question)
                    
                    for opt_data in options_data:
                        option = TestOption(question_id=question.id, **opt_data)
                        db.add(option)
                
                # Комментарии к уроку
                comments = [
                    {"text": "Отличный урок! Очень полезная информация.", "user_id": test_user.id},
                    {"text": "У меня возник вопрос: можно ли использовать JavaScript без веб-браузера?", "user_id": test_user.id}
                ]
                
                for comment_data in comments:
                    comment = LessonComment(lesson_id=lesson.id, **comment_data)
                    db.add(comment)
            
            # Модуль 2: Переменные и типы данных
            module2 = Module(
                course_id=first_course.id,
                title="Переменные и типы данных",
                description="Изучение переменных и основных типов данных в JavaScript",
                order=2
            )
            db.add(module2)
            db.commit()
            db.refresh(module2)
            
            # Уроки для модуля 2
            lessons2 = [
                {
                    "title": "Переменные и константы",
                    "intro_title": "Работа с переменными",
                    "intro_content": "<p>Переменные в JavaScript объявляются с помощью ключевых слов <code>let</code>, <code>const</code> и <code>var</code>.</p><p>В этом уроке мы разберемся с отличиями между ними.</p>",
                    "video_url": "https://www.youtube.com/embed/ix9cRaBkVe0",
                    "video_description": "Подробное объяснение работы с переменными в JavaScript.",
                    "practice_instructions": "<p>Объявите переменные и константы, попробуйте изменить их значения.</p>",
                    "practice_code_template": "// Объявите переменную с помощью let\nlet myVariable = 10;\n\n// Объявите константу с помощью const\nconst myConstant = 'Привет';\n\n// Попробуйте изменить значения\nmyVariable = 20;\n// Что произойдет, если попытаться изменить константу?\n// myConstant = 'Мир';\n",
                    "order": 1,
                    "xp_reward": 30
                },
                {
                    "title": "Типы данных",
                    "intro_title": "Типы данных в JavaScript",
                    "intro_content": "<p>JavaScript имеет несколько основных типов данных: числа, строки, булевы значения, null, undefined, объекты и символы.</p><p>В этом уроке мы рассмотрим каждый из них.</p>",
                    "video_url": "https://www.youtube.com/embed/ix9cRaBkVe0",
                    "video_description": "Детальный обзор всех типов данных в JavaScript.",
                    "practice_instructions": "<p>Определите типы данных разных переменных с помощью оператора typeof.</p>",
                    "practice_code_template": "// Определите типы данных\nlet str = 'Строка';\nlet num = 42;\nlet bool = true;\nlet obj = { name: 'Объект' };\nlet undef;\n\n// Используйте console.log и typeof для вывода типов данных\nconsole.log(typeof str);\n// Проверьте остальные переменные\n",
                    "order": 2,
                    "xp_reward": 35
                }
            ]
            
            for lesson_data in lessons2:
                lesson = Lesson(module_id=module2.id, **lesson_data)
                db.add(lesson)
                db.commit()
                db.refresh(lesson)
                
                # Добавляем прогресс по урокам для пользователя
                if lesson_data["order"] == 1:  # Урок 1 модуля 2 - полностью пройден
                    progress = UserLessonProgress(
                        user_id=test_user.id,
                        lesson_id=lesson.id,
                        intro_completed=True,
                        video_completed=True,
                        practice_completed=True,
                        test_completed=True,
                        test_score=3,
                        earned_xp=lesson_data["xp_reward"],
                        completed=True
                    )
                    db.add(progress)
                elif module2.order == 2 and lesson_data["order"] == 1:  # Урок 1 модуля 2 - в процессе
                    progress = UserLessonProgress(
                        user_id=test_user.id,
                        lesson_id=lesson.id,
                        intro_completed=True,
                        video_completed=True,
                        practice_completed=False,
                        test_completed=False,
                        earned_xp=15,
                        completed=False
                    )
                    db.add(progress)
            
            db.commit()
            print("Модули и уроки успешно созданы.")
            
        print("База данных успешно заполнена тестовыми данными!")
    
    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()