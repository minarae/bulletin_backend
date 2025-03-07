"""initial_migration

Revision ID: cf346f8940b0
Revises:
Create Date: 2024-03-07 05:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cf346f8940b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 시퀀스 생성
    op.execute('CREATE SEQUENCE seq_users START 1')
    op.execute('CREATE SEQUENCE seq_churches START 1')
    op.execute('CREATE SEQUENCE seq_church_admins START 1')
    op.execute('CREATE SEQUENCE seq_bulletin_templates START 1')
    op.execute('CREATE SEQUENCE seq_bulletins START 1')

    # 사용자 테이블 생성
    op.create_table(
        'tb_users',
        sa.Column('id', sa.Integer, server_default=sa.text("nextval('seq_users'::regclass)"), primary_key=True),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('full_name', sa.String),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true')),
        sa.Column('is_superuser', sa.Boolean, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )
    op.create_index('ix_tb_users_id', 'tb_users', ['id'])
    op.create_index('ix_tb_users_email', 'tb_users', ['email'])

    # 교회 테이블 생성
    op.create_table(
        'tb_churches',
        sa.Column('id', sa.Integer, server_default=sa.text("nextval('seq_churches'::regclass)"), primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('address', sa.String),
        sa.Column('contact_info', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )
    op.create_index('ix_tb_churches_id', 'tb_churches', ['id'])
    op.create_index('ix_tb_churches_name', 'tb_churches', ['name'])

    # 교회 관리자 테이블 생성
    op.create_table(
        'tb_church_admins',
        sa.Column('id', sa.Integer, server_default=sa.text("nextval('seq_church_admins'::regclass)"), primary_key=True),
        sa.Column('church_id', sa.Integer, sa.ForeignKey('tb_churches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('tb_users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_tb_church_admins_id', 'tb_church_admins', ['id'])

    # 주보 템플릿 테이블 생성
    op.create_table(
        'tb_bulletin_templates',
        sa.Column('id', sa.Integer, server_default=sa.text("nextval('seq_bulletin_templates'::regclass)"), primary_key=True),
        sa.Column('church_id', sa.Integer, sa.ForeignKey('tb_churches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('template_data', postgresql.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )
    op.create_index('ix_tb_bulletin_templates_id', 'tb_bulletin_templates', ['id'])

    # 주보 테이블 생성
    op.create_table(
        'tb_bulletins',
        sa.Column('id', sa.Integer, server_default=sa.text("nextval('seq_bulletins'::regclass)"), primary_key=True),
        sa.Column('church_id', sa.Integer, sa.ForeignKey('tb_churches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('template_id', sa.Integer, sa.ForeignKey('tb_bulletin_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('content', postgresql.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )
    op.create_index('ix_tb_bulletins_id', 'tb_bulletins', ['id'])
    op.create_index('ix_tb_bulletins_date', 'tb_bulletins', ['date'])


def downgrade() -> None:
    # 테이블 삭제
    op.drop_table('tb_bulletins')
    op.drop_table('tb_bulletin_templates')
    op.drop_table('tb_church_admins')
    op.drop_table('tb_churches')
    op.drop_table('tb_users')

    # 시퀀스 삭제
    op.execute('DROP SEQUENCE seq_bulletins')
    op.execute('DROP SEQUENCE seq_bulletin_templates')
    op.execute('DROP SEQUENCE seq_church_admins')
    op.execute('DROP SEQUENCE seq_churches')
    op.execute('DROP SEQUENCE seq_users')
