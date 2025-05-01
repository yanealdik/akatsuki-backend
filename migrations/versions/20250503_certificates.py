"""Добавляет таблицу для сертификатов

Revision ID: 20250503_certificates
Revises: 20250502_tests_comments
Create Date: 2025-05-03 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '20250503_certificates'
down_revision = '20250502_tests_comments'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу сертификатов
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('issue_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('certificate_url', sa.String(), nullable=True),  # Опциональная ссылка на PDF сертификата
        sa.Column('verification_code', sa.String(), nullable=False),  # Код для проверки подлинности сертификата
        sa.Column('is_valid', sa.Boolean(), default=True, nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'course_id', name='uq_user_course_certificate')
    )
    op.create_index(op.f('ix_certificates_course_id'), 'certificates', ['course_id'], unique=False)
    op.create_index(op.f('ix_certificates_user_id'), 'certificates', ['user_id'], unique=False)
    op.create_index(op.f('ix_certificates_verification_code'), 'certificates', ['verification_code'], unique=True)

def downgrade():
    op.drop_table('certificates')