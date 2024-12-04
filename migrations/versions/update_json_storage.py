"""update json storage

Revision ID: update_json_storage
Revises: fix_json_columns
Create Date: 2024-11-24 16:28:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_json_storage'
down_revision: Union[str, None] = 'fix_json_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update genres column in movies table to use NVARCHAR(max)
    with op.batch_alter_table('movies') as batch_op:
        batch_op.alter_column('genres',
                            existing_type=sa.NVARCHAR(),
                            type_=sa.NVARCHAR(length=None),
                            existing_nullable=True)

    # Update notification_preferences column in watchlist table to use NVARCHAR(max)
    with op.batch_alter_table('watchlist') as batch_op:
        batch_op.alter_column('notification_preferences',
                            existing_type=sa.NVARCHAR(),
                            type_=sa.NVARCHAR(length=None),
                            existing_nullable=True)

    # Update preferences column in Users table to use NVARCHAR(max)
    with op.batch_alter_table('Users') as batch_op:
        batch_op.alter_column('preferences',
                            existing_type=sa.NVARCHAR(),
                            type_=sa.NVARCHAR(length=None),
                            existing_nullable=True)


def downgrade() -> None:
    # Revert genres column in movies table
    with op.batch_alter_table('movies') as batch_op:
        batch_op.alter_column('genres',
                            existing_type=sa.NVARCHAR(length=None),
                            type_=sa.NVARCHAR(),
                            existing_nullable=True)

    # Revert notification_preferences column in watchlist table
    with op.batch_alter_table('watchlist') as batch_op:
        batch_op.alter_column('notification_preferences',
                            existing_type=sa.NVARCHAR(length=None),
                            type_=sa.NVARCHAR(),
                            existing_nullable=True)

    # Revert preferences column in Users table
    with op.batch_alter_table('Users') as batch_op:
        batch_op.alter_column('preferences',
                            existing_type=sa.NVARCHAR(length=None),
                            type_=sa.NVARCHAR(),
                            existing_nullable=True)
