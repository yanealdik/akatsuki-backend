from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime

from app.database import get_db
from app.auth.jwt import get_current_user
from app.auth.models import User
from app.courses.models import Course, UserCourse, CourseStatus
from app.courses.schemas import (
    CourseCreate, CourseResponse, CourseUpdate,
    UserCourseCreate, UserCourseResponse, UserCourseUpdate
)

router = APIRouter(
    prefix="/courses",
    tags=["Курсы"],
)

# Эндпоинты для администраторов (создание и управление курсами)
# В реальном проекте здесь нужно добавить проверку прав доступа

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # В реальной системе здесь должна быть проверка прав доступа
    new_course = Course(**course_data.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/", response_model=List[CourseResponse])
def get_all_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
) -> Any:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    return course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # В реальной системе здесь должна быть проверка прав доступа
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # В реальной системе здесь должна быть проверка прав доступа
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    db.delete(course)
    db.commit()
    return None

# Эндпоинты для пользователей (запись на курсы, отслеживание прогресса)

@router.post("/enroll", response_model=UserCourseResponse)
def enroll_in_course(
    user_course_data: UserCourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == user_course_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    # Проверяем, не записан ли пользователь уже на этот курс
    existing_enrollment = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.id,
        UserCourse.course_id == user_course_data.course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже записаны на этот курс"
        )
    
    # Создаем запись о записи на курс
    new_enrollment = UserCourse(
        user_id=current_user.id,
        course_id=user_course_data.course_id,
        status=CourseStatus.IN_PROGRESS,
        progress=0,
        earned_xp=0
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    
    # Подгружаем информацию о курсе для ответа
    new_enrollment.course = course
    
    return new_enrollment

@router.get("/my-courses", response_model=List[UserCourseResponse])
def get_user_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    user_courses = (
        db.query(UserCourse)
        .filter(UserCourse.user_id == current_user.id)
        .all()
    )
    
    # Загружаем информацию о курсах
    for user_course in user_courses:
        course = db.query(Course).filter(Course.id == user_course.course_id).first()
        user_course.course = course
    
    return user_courses

@router.get("/my-courses/{course_id}", response_model=UserCourseResponse)
def get_user_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    user_course = (
        db.query(UserCourse)
        .filter(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        )
        .first()
    )
    
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не записаны на этот курс"
        )
    
    # Загружаем информацию о курсе
    course = db.query(Course).filter(Course.id == user_course.course_id).first()
    user_course.course = course
    
    return user_course

@router.put("/my-courses/{course_id}", response_model=UserCourseResponse)
def update_course_progress(
    course_id: int,
    update_data: UserCourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Находим запись о курсе пользователя
    user_course = (
        db.query(UserCourse)
        .filter(
            UserCourse.user_id == current_user.id,
            UserCourse.course_id == course_id
        )
        .first()
    )
    
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не записаны на этот курс"
        )
    
    # Получаем информацию о курсе
    course = db.query(Course).filter(Course.id == course_id).first()
    
    # Обновляем данные о прогрессе
    if update_data.progress is not None:
        user_course.progress = update_data.progress
    
    # Если статус изменился на COMPLETED
    if update_data.status == CourseStatus.COMPLETED and user_course.status != CourseStatus.COMPLETED:
        user_course.status = CourseStatus.COMPLETED
        user_course.completed_at = datetime.utcnow()
        user_course.progress = 100
        
        # Начисляем XP за прохождение курса
        user_course.earned_xp = course.xp_reward
        
        # Обновляем общее количество XP пользователя
        current_user.xp += course.xp_reward
        db.add(current_user)
    
    db.add(user_course)
    db.commit()
    db.refresh(user_course)
    
    # Загружаем информацию о курсе для ответа
    user_course.course = course
    
    return user_course