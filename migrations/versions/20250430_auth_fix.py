"""add_user_active_default

Revision ID: 20250430_auth_fix
Revises: 20250427_add_verification
Create Date: 2025-04-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250430_auth_fix'
down_revision = '20250427_add_verification'
branch_labels = None
depends_on = None


def upgrade():
    # Проверяем существование колонки is_active в таблице users
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('users')
    column_names = [c['name'] for c in columns]
    
    if 'is_active' in column_names:
        # Изменяем is_active на True по умолчанию
        op.alter_column('users', 'is_active',
                        server_default=sa.text('true'),
                        existing_type=sa.Boolean(),
                        nullable=False)
    
    if 'is_verified' in column_names:
        # Изменяем is_verified на True по умолчанию
        op.alter_column('users', 'is_verified',
                        server_default=sa.text('true'),
                        existing_type=sa.Boolean(),
                        nullable=False)
    
    # Обновляем существующие записи
    op.execute("UPDATE users SET is_active = true, is_verified = true WHERE is_active = false OR is_verified = false")


def downgrade():
    # Проверяем существование колонок
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('users')
    column_names = [c['name'] for c in columns]
    
    # Возвращаем к исходному состоянию
    if 'is_active' in column_names:
        op.alter_column('users', 'is_active',
                        server_default=sa.text('false'),
                        existing_type=sa.Boolean(),
                        nullable=False)
    
    if 'is_verified' in column_names:
        op.alter_column('users', 'is_verified',
                        server_default=sa.text('false'),
                        existing_type=sa.Boolean(),
                        nullable=False)