"""fix json columns

Revision ID: fix_json_columns
Revises: fix_column_types
Create Date: 2024-11-24 16:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import JSON


# revision identifiers, used by Alembic.
revision: str = 'fix_json_columns'
down_revision: Union[str, None] = 'fix_column_types'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop and recreate genres column in movies table
    with op.batch_alter_table('movies') as batch_op:
        batch_op.drop_column('genres')
        batch_op.add_column(sa.Column('genres', JSON(), nullable=True))

    # Drop and recreate notification_preferences column in watchlist table
    with op.batch_alter_table('watchlist') as batch_op:
        batch_op.drop_column('notification_preferences')
        batch_op.add_column(sa.Column('notification_preferences', JSON(), nullable=True))


def downgrade() -> None:
    # Revert genres column in movies table
    with op.batch_alter_table('movies') as batch_op:
        batch_op.drop_column('genres')
        batch_op.add_column(sa.Column('genres', sa.NVARCHAR(), nullable=True))

    # Revert notification_preferences column in watchlist table
    with op.batch_alter_table('watchlist') as batch_op:
        batch_op.drop_column('notification_preferences')
        batch_op.add_column(sa.Column('notification_preferences', sa.NVARCHAR(), nullable=True))
