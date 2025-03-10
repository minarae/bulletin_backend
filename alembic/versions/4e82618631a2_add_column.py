"""add_column

Revision ID: 4e82618631a2
Revises: cf346f8940b0
Create Date: 2025-03-10 14:42:49.017265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4e82618631a2'
down_revision: Union[str, None] = 'cf346f8940b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tb_users', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('tb_users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE tb_users SET is_deleted = FALSE")
    op.alter_column('tb_users', 'is_deleted', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tb_users', 'deleted_at')
    op.drop_column('tb_users', 'is_deleted')
    # ### end Alembic commands ###
