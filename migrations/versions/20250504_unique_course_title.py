"""add_unique_constraint_to_courses

Revision ID: 20250504_unique_course_title
Revises: 20250503_certificates
Create Date: 2025-05-04 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250504_unique_course_title'
down_revision = '20250503_certificates'
branch_labels = None
depends_on = None


def upgrade():
    # Проверяем, существует ли уже ограничение
    conn = op.get_bind()
    query = sa.text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE constraint_name = 'unique_course_title'
        AND table_name = 'courses'
        AND constraint_type = 'UNIQUE'
    """)
    result = conn.execute(query).fetchone()
    
    if not result:
        # Добавляем уникальное ограничение на столбец title
        op.create_unique_constraint(
            'unique_course_title',
            'courses',
            ['title']
        )
        print("Добавлено уникальное ограничение для столбца title в таблице courses")
    else:
        print("Уникальное ограничение для столбца title в таблице courses уже существует")


def downgrade():
    # Проверяем, существует ли ограничение
    conn = op.get_bind()
    query = sa.text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE constraint_name = 'unique_course_title'
        AND table_name = 'courses'
        AND constraint_type = 'UNIQUE'
    """)
    result = conn.execute(query).fetchone()
    
    if result:
        # Удаляем уникальное ограничение
        op.drop_constraint(
            'unique_course_title',
            'courses',
            type_='unique'
        )
        print("Удалено уникальное ограничение для столбца title в таблице courses")
    else:
        print("Уникальное ограничение для столбца title в таблице courses не существует")