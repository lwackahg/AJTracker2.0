"""update tables safely

Revision ID: update_tables_safe
Revises: update_all_tables
Create Date: 2024-11-24 16:21:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_tables_safe'
down_revision: Union[str, None] = 'update_all_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tables only if they don't exist
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()

    # watchlist table
    if 'watchlist' not in existing_tables:
        op.create_table('watchlist',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('userID', sa.Integer(), nullable=False),
            sa.Column('movieID', sa.Integer(), nullable=False),
            sa.Column('added_date', sa.DateTime(), nullable=True),
            sa.Column('notification_preferences', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['movieID'], ['movies.movieID'], ),
            sa.ForeignKeyConstraint(['userID'], ['Users.UserId'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # watch_history table
    if 'watch_history' not in existing_tables:
        op.create_table('watch_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('userID', sa.Integer(), nullable=False),
            sa.Column('movieID', sa.Integer(), nullable=False),
            sa.Column('watched_date', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['movieID'], ['movies.movieID'], ),
            sa.ForeignKeyConstraint(['userID'], ['Users.UserId'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # read_history table
    if 'read_history' not in existing_tables:
        op.create_table('read_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('userID', sa.Integer(), nullable=False),
            sa.Column('bookID', sa.Integer(), nullable=False),
            sa.Column('read_date', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['bookID'], ['Books.BookId'], ),
            sa.ForeignKeyConstraint(['userID'], ['Users.UserId'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Add any missing columns to existing tables if needed
    if 'movies' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('movies')]
        
        if 'average_rating' not in columns:
            op.add_column('movies', sa.Column('average_rating', sa.Float(), nullable=True))
        
        if 'genres' not in columns:
            op.add_column('movies', sa.Column('genres', sa.JSON(), nullable=True))
        
        if 'runtime' not in columns:
            op.add_column('movies', sa.Column('runtime', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Drop tables in reverse order to handle dependencies
    op.drop_table('read_history')
    op.drop_table('watch_history')
    op.drop_table('watchlist')
