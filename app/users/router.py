from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.auth.jwt import get_current_user
from app.auth.models import User
from app.courses.models import UserCourse, Course
from app.courses.schemas import UserProfile, UserCourseBrief

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router.get("/profile", response_model=UserProfile)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение профиля текущего пользователя с информацией о курсах
    """
    # Получаем курсы пользователя
    user_courses = (
        db.query(UserCourse, Course.title)
        .join(Course, UserCourse.course_id == Course.id)
        .filter(UserCourse.user_id == current_user.id)
        .all()
    )
    
    # Преобразуем в формат для ответа
    courses_data = []
    for user_course, course_title in user_courses:
        courses_data.append(
            UserCourseBrief(
                id=user_course.id,
                course_id=user_course.course_id,
                title=course_title,
                status=user_course.status,
                progress=user_course.progress,
                earned_xp=user_course.earned_xp
            )
        )
    
    # Создаем полный профиль пользователя
    user_profile = UserProfile(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        xp=current_user.xp,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        courses=courses_data
    )
    
    return user_profile

@router.get("/{user_id}/profile", response_model=UserProfile)
def get_user_profile_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение профиля пользователя по ID (для публичных профилей)
    В реальной системе здесь должна быть проверка прав доступа
    """
    # Получаем пользователя
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Получаем курсы пользователя
    user_courses = (
        db.query(UserCourse, Course.title)
        .join(Course, UserCourse.course_id == Course.id)
        .filter(UserCourse.user_id == user_id)
        .all()
    )
    
    # Преобразуем в формат для ответа
    courses_data = []
    for user_course, course_title in user_courses:
        courses_data.append(
            UserCourseBrief(
                id=user_course.id,
                course_id=user_course.course_id,
                title=course_title,
                status=user_course.status,
                progress=user_course.progress,
                earned_xp=user_course.earned_xp
            )
        )
    
    # Создаем полный профиль пользователя
    user_profile = UserProfile(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        xp=user.xp,
        is_active=user.is_active,
        created_at=user.created_at,
        courses=courses_data
    )
    
    return user_profile

@router.get("/leaderboard", response_model=list[dict])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Any:
    """
    Получение таблицы лидеров по XP
    """
    leaderboard = (
        db.query(User.id, User.nickname, User.xp)
        .order_by(User.xp.desc())
        .limit(limit)
        .all()
    )
    
    result = []
    for i, (user_id, nickname, xp) in enumerate(leaderboard, 1):
        result.append({
            "rank": i,
            "user_id": user_id,
            "nickname": nickname,
            "xp": xp
        })
    
    return result