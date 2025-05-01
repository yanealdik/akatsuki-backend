from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class CourseStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Схемы для курсов
class CourseBase(BaseModel):
    title: str
    description: str
    duration: int
    xp_reward: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    xp_reward: Optional[int] = None

class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Схемы для связи пользователь-курс
class UserCourseCreate(BaseModel):
    course_id: int

class UserCourseUpdate(BaseModel):
    progress: Optional[int] = None
    status: Optional[CourseStatus] = None

class UserCourseResponse(BaseModel):
    id: int
    course_id: int
    status: CourseStatus
    progress: int
    earned_xp: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    course: CourseResponse

    class Config:
        orm_mode = True

# Схемы для модулей
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int

class ModuleCreate(ModuleBase):
    course_id: int

class ModuleUpdate(ModuleBase):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

class ModuleResponse(ModuleBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Схемы для уроков
class LessonBase(BaseModel):
    title: str
    intro_title: Optional[str] = None
    intro_content: Optional[str] = None
    video_url: Optional[str] = None
    video_description: Optional[str] = None
    practice_instructions: Optional[str] = None
    practice_code_template: Optional[str] = None
    order: int
    xp_reward: int

class LessonCreate(LessonBase):
    module_id: int

class LessonUpdate(LessonBase):
    title: Optional[str] = None
    intro_title: Optional[str] = None
    intro_content: Optional[str] = None
    video_url: Optional[str] = None
    video_description: Optional[str] = None
    practice_instructions: Optional[str] = None
    practice_code_template: Optional[str] = None
    order: Optional[int] = None
    xp_reward: Optional[int] = None

class LessonIntro(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class LessonVideo(BaseModel):
    url: Optional[str] = None
    description: Optional[str] = None

class LessonPractice(BaseModel):
    instructions: Optional[str] = None
    codeTemplate: Optional[str] = None

class TestQuestionOption(BaseModel):
    id: int
    text: str

class TestQuestion(BaseModel):
    id: int
    question: str
    options: List[TestQuestionOption]

class LessonProgress(BaseModel):
    intro_completed: bool
    video_completed: bool
    practice_completed: bool
    test_completed: bool
    test_score: Optional[int] = None
    earned_xp: int
    completed: bool

class LessonResponse(BaseModel):
    id: int
    title: str
    module_id: int
    intro: LessonIntro
    video: LessonVideo
    practice: LessonPractice
    test: List[TestQuestion]
    xp_reward: int
    progress: Optional[LessonProgress] = None

    class Config:
        orm_mode = True

# Схемы для обновления прогресса
class LessonProgressUpdate(BaseModel):
    section: str = Field(..., description="Секция урока (intro, video, practice, test)")
    completed: bool = Field(..., description="Статус завершения секции")
    xp: Optional[int] = Field(None, description="Дополнительные XP за секцию")

# Схемы для тестов
class TestSubmission(BaseModel):
    answers: Dict[str, str] = Field(..., description="Словарь с ответами на вопросы (question_id: option_id)")

class TestResult(BaseModel):
    score: int
    total: int
    passed: bool
    message: str

# Схемы для комментариев
class CommentCreate(BaseModel):
    text: str
    parent_id: Optional[int] = None

class UserBrief(BaseModel):
    id: int
    nickname: str

class CommentResponse(BaseModel):
    id: int
    text: str
    user: UserBrief
    created_at: datetime
    likes_count: int
    parent_id: Optional[int] = None
    replies: Optional[List['CommentResponse']] = None

    class Config:
        orm_mode = True

# Схемы для профиля пользователя
class UserCourseBrief(BaseModel):
    id: int
    course_id: int
    title: str
    status: CourseStatus
    progress: int
    earned_xp: int

class UserProfile(BaseModel):
    id: int
    email: str
    nickname: str
    xp: int
    is_active: bool
    created_at: datetime
    courses: List[UserCourseBrief]

    class Config:
        orm_mode = True

# Схемы для сертификатов
class CertificateCreate(BaseModel):
    course_id: int

class CertificateResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    issue_date: datetime
    verification_code: str
    certificate_url: Optional[str] = None

    class Config:
        orm_mode = True