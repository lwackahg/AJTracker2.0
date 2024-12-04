"""fix column types

Revision ID: fix_column_types
Revises: update_tables_safe
Create Date: 2024-11-24 16:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_column_types'
down_revision: Union[str, None] = 'update_tables_safe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add movieID column to MovieAdaptations if it doesn't exist
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    movie_adaptations_columns = [col['name'] for col in inspector.get_columns('MovieAdaptations')]
    
    if 'movieID' not in movie_adaptations_columns:
        op.add_column('MovieAdaptations', sa.Column('movieID', sa.Integer(), nullable=True))
        op.create_foreign_key(None, 'MovieAdaptations', 'movies', ['movieID'], ['movieID'])

    # Fix genres column in movies table
    with op.batch_alter_table('movies') as batch_op:
        batch_op.alter_column('genres',
                            existing_type=sa.NVARCHAR(),
                            type_=sa.JSON(),
                            existing_nullable=True)

    # Fix notification_preferences column in watchlist table
    with op.batch_alter_table('watchlist') as batch_op:
        batch_op.alter_column('notification_preferences',
                            existing_type=sa.NVARCHAR(),
                            type_=sa.JSON(),
                            existing_nullable=True)


def downgrade() -> None:
    # Revert genres column in movies table
    with op.batch_alter_table('movies') as batch_op:
        batch_op.alter_column('genres',
                            existing_type=sa.JSON(),
                            type_=sa.NVARCHAR(),
                            existing_nullable=True)

    # Revert notification_preferences column in watchlist table
    with op.batch_alter_table('watchlist') as batch_op:
        batch_op.alter_column('notification_preferences',
                            existing_type=sa.JSON(),
                            type_=sa.NVARCHAR(),
                            existing_nullable=True)

    # Remove movieID column from MovieAdaptations
    op.drop_constraint(None, 'MovieAdaptations', type_='foreignkey')
    op.drop_column('MovieAdaptations', 'movieID')
