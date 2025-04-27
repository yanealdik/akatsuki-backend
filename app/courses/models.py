from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class CourseStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # Продолжительность в минутах
    xp_reward = Column(Integer, nullable=False, default=0)  # XP за прохождение курса
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь с пользователями через таблицу user_courses
    users = relationship("UserCourse", back_populates="course")

class UserCourse(Base):
    __tablename__ = "user_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(CourseStatus), default=CourseStatus.IN_PROGRESS, nullable=False)
    progress = Column(Integer, default=0)  # Прогресс в процентах
    earned_xp = Column(Integer, default=0)  # Заработанные XP за курс
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Обратные отношения
    course = relationship("Course", back_populates="users")
    user = relationship("User", backref="courses")