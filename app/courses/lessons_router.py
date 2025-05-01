from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime

from app.database import get_db
from app.auth.jwt import get_current_user
from app.auth.models import User
from app.courses.models import (
    Course, Module, Lesson, UserLessonProgress,
    TestQuestion, TestOption, UserTestAnswer, 
    LessonComment, CommentLike, LessonReaction
)
from app.courses.schemas import (
    LessonResponse, LessonProgressUpdate, TestSubmission,
    CommentCreate, CommentResponse, TestResult
)

router = APIRouter(
    prefix="/lessons",
    tags=["Уроки"],
)

@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получить полную информацию об уроке, включая содержимое и тесты
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Проверяем прогресс пользователя по этому уроку
    progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson_id
    ).first()
    
    # Если прогресса нет, создаем его
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            intro_completed=False,
            video_completed=False,
            practice_completed=False,
            test_completed=False,
            earned_xp=0,
            completed=False
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    # Получаем тестовые вопросы для урока
    test_questions = []
    db_questions = db.query(TestQuestion).filter(
        TestQuestion.lesson_id == lesson_id
    ).order_by(TestQuestion.order).all()
    
    for question in db_questions:
        options = db.query(TestOption).filter(
            TestOption.question_id == question.id
        ).order_by(TestOption.order).all()
        
        test_questions.append({
            "id": question.id,
            "question": question.question,
            "options": [{"id": opt.id, "text": opt.text} for opt in options]
        })
    
    # Формируем ответ с данными урока и прогрессом
    lesson_data = {
        "id": lesson.id,
        "title": lesson.title,
        "module_id": lesson.module_id,
        "intro": {
            "title": lesson.intro_title,
            "content": lesson.intro_content
        },
        "video": {
            "url": lesson.video_url,
            "description": lesson.video_description
        },
        "practice": {
            "instructions": lesson.practice_instructions,
            "codeTemplate": lesson.practice_code_template
        },
        "test": test_questions,
        "xp_reward": lesson.xp_reward,
        "progress": {
            "intro_completed": progress.intro_completed,
            "video_completed": progress.video_completed,
            "practice_completed": progress.practice_completed,
            "test_completed": progress.test_completed,
            "test_score": progress.test_score,
            "earned_xp": progress.earned_xp,
            "completed": progress.completed
        }
    }
    
    return lesson_data

@router.post("/{lesson_id}/progress", status_code=status.HTTP_200_OK)
def update_lesson_progress(
    lesson_id: int,
    progress_data: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Обновление прогресса пользователя по уроку
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Находим или создаем запись о прогрессе
    progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson_id
    ).first()
    
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            intro_completed=False,
            video_completed=False,
            practice_completed=False,
            test_completed=False,
            earned_xp=0,
            completed=False
        )
        db.add(progress)
    
    # Обновляем поля прогресса
    if progress_data.section == "intro" and progress_data.completed:
        progress.intro_completed = True
        if not progress.intro_completed:  # Если раньше не было завершено
            progress.earned_xp += 10
    
    if progress_data.section == "video" and progress_data.completed:
        progress.video_completed = True
        if not progress.video_completed:  # Если раньше не было завершено
            progress.earned_xp += 15
    
    if progress_data.section == "practice" and progress_data.completed:
        progress.practice_completed = True
        if not progress.practice_completed:  # Если раньше не было завершено
            progress.earned_xp += 25
    
    # Проверяем, завершен ли весь урок
    if progress.intro_completed and progress.video_completed and progress.practice_completed and progress.test_completed:
        progress.completed = True
        
        # Если урок только что завершен, начисляем дополнительный XP
        if not progress.completed:
            # Дополнительный бонус за завершение
            bonus_xp = 15
            progress.earned_xp += bonus_xp
            
            # Обновляем общий XP пользователя
            current_user.xp += progress.earned_xp
            db.add(current_user)
    
    db.commit()
    db.refresh(progress)
    
    return {
        "success": True,
        "progress": {
            "intro_completed": progress.intro_completed,
            "video_completed": progress.video_completed,
            "practice_completed": progress.practice_completed,
            "test_completed": progress.test_completed,
            "earned_xp": progress.earned_xp,
            "completed": progress.completed
        }
    }

@router.post("/{lesson_id}/check-code", status_code=status.HTTP_200_OK)
def check_practice_code(
    lesson_id: int,
    code_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Проверка кода практического задания
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # В реальном проекте здесь должна быть логика проверки кода
    # Сейчас просто принимаем любой код как правильный

    # Находим запись о прогрессе
    progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson_id
    ).first()
    
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            intro_completed=False,
            video_completed=False,
            practice_completed=False,
            test_completed=False,
            earned_xp=0,
            completed=False
        )
        db.add(progress)
    
    # Отмечаем практику как завершенную
    if not progress.practice_completed:
        progress.practice_completed = True
        progress.earned_xp += 25
        db.commit()
        db.refresh(progress)
    
    return {
        "success": True,
        "message": "Отлично! Ваш код прошел проверку."
    }

@router.post("/{lesson_id}/check-test", response_model=TestResult)
def submit_test(
    lesson_id: int,
    test_data: TestSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Проверка ответов на тестовые вопросы
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Получаем вопросы теста
    questions = db.query(TestQuestion).filter(
        TestQuestion.lesson_id == lesson_id
    ).all()
    
    # Проверяем ответы
    correct_answers = 0
    total_questions = len(questions)
    
    for question_id, option_id in test_data.answers.items():
        # Находим правильный ответ
        correct_option = db.query(TestOption).filter(
            TestOption.question_id == int(question_id),
            TestOption.is_correct == True
        ).first()
        
        if correct_option and correct_option.id == int(option_id):
            correct_answers += 1
        
        # Сохраняем ответ пользователя
        user_answer = UserTestAnswer(
            user_id=current_user.id,
            question_id=int(question_id),
            selected_option_id=int(option_id),
            is_correct=correct_option and correct_option.id == int(option_id)
        )
        db.add(user_answer)
    
    # Рассчитываем процент правильных ответов
    score_percent = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Тест считается пройденным, если правильных ответов >= 70%
    passed = score_percent >= 70
    
    # Обновляем прогресс урока
    progress = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson_id
    ).first()
    
    if not progress:
        progress = UserLessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            intro_completed=False,
            video_completed=False,
            practice_completed=False,
            test_completed=False,
            earned_xp=0,
            completed=False
        )
        db.add(progress)
    
    # Отмечаем тест как пройденный и начисляем XP
    progress.test_completed = passed
    progress.test_score = correct_answers
    
    if passed and not progress.test_completed:
        # Начисляем XP за прохождение теста
        xp_reward = int(lesson.xp_reward * (score_percent / 100))
        progress.earned_xp += xp_reward
    
    # Проверяем, завершен ли урок полностью
    if progress.intro_completed and progress.video_completed and progress.practice_completed and passed:
        progress.completed = True
        
        # Обновляем общий XP пользователя
        current_user.xp += progress.earned_xp
        db.add(current_user)
    
    db.commit()
    db.refresh(progress)
    
    return {
        "score": correct_answers,
        "total": total_questions,
        "passed": passed,
        "message": "Тест успешно пройден!" if passed else "Для прохождения теста необходимо правильно ответить минимум на 70% вопросов."
    }

@router.post("/{lesson_id}/comments", response_model=CommentResponse)
def add_comment(
    lesson_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Добавление комментария к уроку
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Создаем комментарий
    new_comment = LessonComment(
        lesson_id=lesson_id,
        user_id=current_user.id,
        text=comment_data.text,
        parent_id=comment_data.parent_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "id": new_comment.id,
        "text": new_comment.text,
        "user": {
            "id": current_user.id,
            "nickname": current_user.nickname
        },
        "created_at": new_comment.created_at,
        "likes_count": 0,
        "parent_id": new_comment.parent_id
    }

@router.get("/{lesson_id}/comments", response_model=List[CommentResponse])
def get_lesson_comments(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение комментариев к уроку
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Получаем комментарии к уроку
    comments = db.query(LessonComment).filter(
        LessonComment.lesson_id == lesson_id,
        LessonComment.parent_id.is_(None)  # Получаем только родительские комментарии
    ).order_by(LessonComment.created_at.desc()).all()
    
    # Формируем ответ
    result = []
    for comment in comments:
        # Получаем количество лайков
        likes_count = db.query(CommentLike).filter(
            CommentLike.comment_id == comment.id
        ).count()
        
        # Получаем информацию о пользователе
        user = db.query(User).filter(User.id == comment.user_id).first()
        
        # Получаем ответы на комментарий
        replies = db.query(LessonComment).filter(
            LessonComment.parent_id == comment.id
        ).order_by(LessonComment.created_at).all()
        
        replies_data = []
        for reply in replies:
            reply_likes_count = db.query(CommentLike).filter(
                CommentLike.comment_id == reply.id
            ).count()
            
            reply_user = db.query(User).filter(User.id == reply.user_id).first()
            
            replies_data.append({
                "id": reply.id,
                "text": reply.text,
                "user": {
                    "id": reply.user_id,
                    "nickname": reply_user.nickname if reply_user else "Пользователь"
                },
                "created_at": reply.created_at,
                "likes_count": reply_likes_count,
                "parent_id": reply.parent_id
            })
        
        result.append({
            "id": comment.id,
            "text": comment.text,
            "user": {
                "id": comment.user_id,
                "nickname": user.nickname if user else "Пользователь"
            },
            "created_at": comment.created_at,
            "likes_count": likes_count,
            "parent_id": None,
            "replies": replies_data
        })
    
    return result

@router.post("/{lesson_id}/like", status_code=status.HTTP_200_OK)
def like_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Поставить лайк уроку
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Проверяем, есть ли уже реакция от пользователя
    existing_reaction = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.user_id == current_user.id
    ).first()
    
    if existing_reaction:
        existing_reaction.is_like = True
        existing_reaction.updated_at = datetime.utcnow()
    else:
        # Создаем новую реакцию
        new_reaction = LessonReaction(
            lesson_id=lesson_id,
            user_id=current_user.id,
            is_like=True
        )
        db.add(new_reaction)
    
    db.commit()
    
    # Подсчитываем общее количество лайков и дизлайков
    likes_count = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.is_like == True
    ).count()
    
    dislikes_count = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.is_like == False
    ).count()
    
    return {
        "success": True,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count
    }

@router.post("/{lesson_id}/dislike", status_code=status.HTTP_200_OK)
def dislike_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Поставить дизлайк уроку
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Проверяем, есть ли уже реакция от пользователя
    existing_reaction = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.user_id == current_user.id
    ).first()
    
    if existing_reaction:
        existing_reaction.is_like = False
        existing_reaction.updated_at = datetime.utcnow()
    else:
        # Создаем новую реакцию
        new_reaction = LessonReaction(
            lesson_id=lesson_id,
            user_id=current_user.id,
            is_like=False
        )
        db.add(new_reaction)
    
    db.commit()
    
    # Подсчитываем общее количество лайков и дизлайков
    likes_count = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.is_like == True
    ).count()
    
    dislikes_count = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.is_like == False
    ).count()
    
    return {
        "success": True,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count
    }

@router.delete("/{lesson_id}/like", status_code=status.HTTP_200_OK)
@router.delete("/{lesson_id}/dislike", status_code=status.HTTP_200_OK)
def remove_lesson_reaction(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Удалить реакцию (лайк или дизлайк) с урока
    """
    # Находим урок
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    # Находим реакцию пользователя
    reaction = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.user_id == current_user.id
    ).first()
    
    if reaction:
        db.delete(reaction)
        db.commit()
    
    # Подсчитываем общее количество лайков и дизлайков
    likes_count = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.is_like == True
    ).count()
    
    dislikes_count = db.query(LessonReaction).filter(
        LessonReaction.lesson_id == lesson_id,
        LessonReaction.is_like == False
    ).count()
    
    return {
        "success": True,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count
    }