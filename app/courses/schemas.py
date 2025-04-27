from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.courses.models import CourseStatus

class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str
    duration: int = Field(..., gt=0)  # Продолжительность в минутах
    xp_reward: int = Field(..., ge=0)  # XP за прохождение курса

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, gt=0)
    xp_reward: Optional[int] = Field(None, ge=0)

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserCourseBase(BaseModel):
    course_id: int
    status: CourseStatus = CourseStatus.IN_PROGRESS
    progress: int = Field(0, ge=0, le=100)  # Прогресс в процентах

class UserCourseCreate(UserCourseBase):
    pass

class UserCourseUpdate(BaseModel):
    status: Optional[CourseStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)

class UserCourseResponse(UserCourseBase):
    id: int
    user_id: int
    earned_xp: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    course: CourseResponse

    class Config:
        orm_mode = True

class UserCourseBrief(BaseModel):
    id: int
    course_id: int
    title: str
    status: CourseStatus
    progress: int
    earned_xp: int
    
    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    id: int
    email: str
    nickname: str
    xp: int
    is_active: bool
    created_at: datetime
    courses: List[UserCourseBrief] = []
    
    class Config:
        orm_mode = True