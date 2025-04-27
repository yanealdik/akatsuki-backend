"""add_verification_codes

Revision ID: 20250427_add_verification
Revises: 
Create Date: 2025-04-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250427_add_verification'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем поле is_verified в таблицу пользователей
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='False'))
    
    # Создаем таблицу для кодов верификации
    op.create_table('verification_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='False'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем индексы для таблицы верификации кодов
    op.create_index(op.f('ix_verification_codes_email'), 'verification_codes', ['email'], unique=False)
    op.create_index(op.f('ix_verification_codes_id'), 'verification_codes', ['id'], unique=False)
    op.create_index(op.f('ix_verification_codes_user_id'), 'verification_codes', ['user_id'], unique=False)


def downgrade():
    # Удаляем таблицу кодов верификации и индексы
    op.drop_index(op.f('ix_verification_codes_user_id'), table_name='verification_codes')
    op.drop_index(op.f('ix_verification_codes_id'), table_name='verification_codes')
    op.drop_index(op.f('ix_verification_codes_email'), table_name='verification_codes')
    op.drop_table('verification_codes')
    
    # Удаляем поле is_verified из таблицы пользователей
    op.drop_column('users', 'is_verified')