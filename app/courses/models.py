from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
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
    # Связь с модулями курса
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")

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

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, index=True, nullable=False)  # Порядок модуля в курсе
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String, nullable=False)
    intro_title = Column(String, nullable=True)
    intro_content = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    video_description = Column(Text, nullable=True)
    practice_instructions = Column(Text, nullable=True)
    practice_code_template = Column(Text, nullable=True)
    order = Column(Integer, index=True, nullable=False)  # Порядок урока в модуле
    xp_reward = Column(Integer, nullable=False, default=0)  # XP за прохождение урока
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    module = relationship("Module", back_populates="lessons")
    user_progress = relationship("UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    test_questions = relationship("TestQuestion", back_populates="lesson", cascade="all, delete-orphan")
    comments = relationship("LessonComment", back_populates="lesson", cascade="all, delete-orphan")
    reactions = relationship("LessonReaction", back_populates="lesson", cascade="all, delete-orphan")

class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)
    intro_completed = Column(Boolean, default=False, nullable=False)
    video_completed = Column(Boolean, default=False, nullable=False)
    practice_completed = Column(Boolean, default=False, nullable=False)
    test_completed = Column(Boolean, default=False, nullable=False)
    test_score = Column(Integer, nullable=True)
    earned_xp = Column(Integer, default=0, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Связи с другими таблицами
    lesson = relationship("Lesson", back_populates="user_progress")
    user = relationship("User", backref="lesson_progress")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

class TestQuestion(Base):
    __tablename__ = "test_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)
    question = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи с другими таблицами
    lesson = relationship("Lesson", back_populates="test_questions")
    options = relationship("TestOption", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserTestAnswer", back_populates="question", cascade="all, delete-orphan")

class TestOption(Base):
    __tablename__ = "test_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("test_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, nullable=False)
    
    # Связи с другими таблицами
    question = relationship("TestQuestion", back_populates="options")
    user_answers = relationship("UserTestAnswer", back_populates="selected_option")

class UserTestAnswer(Base):
    __tablename__ = "user_test_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("test_questions.id", ondelete="CASCADE"), index=True, nullable=False)
    selected_option_id = Column(Integer, ForeignKey("test_options.id", ondelete="CASCADE"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи с другими таблицами
    question = relationship("TestQuestion", back_populates="user_answers")
    selected_option = relationship("TestOption", back_populates="user_answers")
    user = relationship("User", backref="test_answers")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

class LessonComment(Base):
    __tablename__ = "lesson_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    text = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("lesson_comments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    lesson = relationship("Lesson", back_populates="comments")
    user = relationship("User", backref="comments")
    # Исправленное определение отношения для вложенных комментариев
    replies = relationship("LessonComment", backref=backref("parent", remote_side=[id]))
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")

class CommentLike(Base):
    __tablename__ = "comment_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("lesson_comments.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи с другими таблицами
    comment = relationship("LessonComment", back_populates="likes")
    user = relationship("User", backref="comment_likes")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

class LessonReaction(Base):
    __tablename__ = "lesson_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    is_like = Column(Boolean, nullable=False)  # True для лайка, False для дизлайка
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    lesson = relationship("Lesson", back_populates="reactions")
    user = relationship("User", backref="lesson_reactions")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    issue_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    certificate_url = Column(String, nullable=True)
    verification_code = Column(String, index=True, nullable=False, unique=True)
    is_valid = Column(Boolean, default=True, nullable=False)
    
    # Связи с другими таблицами
    user = relationship("User", backref="certificates")
    course = relationship("Course", backref="certificates")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )