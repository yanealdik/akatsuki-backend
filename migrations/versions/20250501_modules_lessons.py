"""Добавляет таблицы для модулей и уроков

Revision ID: 20250501_modules_lessons
Revises: 20250430_auth_fix
Create Date: 2025-05-01 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '20250501_modules_lessons'
down_revision = '20250430_auth_fix'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу модулей курса
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modules_course_id'), 'modules', ['course_id'], unique=False)
    op.create_index(op.f('ix_modules_order'), 'modules', ['order'], unique=False)

    # Создаем таблицу уроков
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('intro_title', sa.String(), nullable=True),
        sa.Column('intro_content', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('video_description', sa.Text(), nullable=True),
        sa.Column('practice_instructions', sa.Text(), nullable=True),
        sa.Column('practice_code_template', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('xp_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lessons_module_id'), 'lessons', ['module_id'], unique=False)
    op.create_index(op.f('ix_lessons_order'), 'lessons', ['order'], unique=False)

    # Создаем таблицу для отслеживания прогресса по урокам
    op.create_table(
        'user_lesson_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('intro_completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('video_completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('practice_completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('test_completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('test_score', sa.Integer(), nullable=True),
        sa.Column('earned_xp', sa.Integer(), default=0, nullable=False),
        sa.Column('completed', sa.Boolean(), default=False, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson')
    )
    op.create_index(op.f('ix_user_lesson_progress_lesson_id'), 'user_lesson_progress', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_user_lesson_progress_user_id'), 'user_lesson_progress', ['user_id'], unique=False)

def downgrade():
    op.drop_table('user_lesson_progress')
    op.drop_table('lessons')
    op.drop_table('modules')