"""update all tables

Revision ID: update_all_tables
Revises: 7d4b2b0c5749
Create Date: 2024-11-24 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'update_all_tables'
down_revision = '7d4b2b0c5749'
branch_labels = None
depends_on = None

def upgrade():
    # Create movies table
    op.create_table('movies',
        sa.Column('movieID', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('releaseDate', sa.Date(), nullable=True),
        sa.Column('overview', sa.Text(), nullable=True),
        sa.Column('tmdb_id', sa.Integer(), nullable=True),
        sa.Column('genres', mssql.JSON(), nullable=True),
        sa.Column('runtime', sa.Integer(), nullable=True),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('movieID'),
        sa.UniqueConstraint('tmdb_id')
    )

    # Create watchlist table
    op.create_table('watchlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('userID', sa.Integer(), nullable=False),
        sa.Column('movieID', sa.Integer(), nullable=False),
        sa.Column('added_date', sa.DateTime(), nullable=True),
        sa.Column('notification_preferences', mssql.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['movieID'], ['movies.movieID'], ),
        sa.ForeignKeyConstraint(['userID'], ['Users.UserId'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create watch_history table
    op.create_table('watch_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('userID', sa.Integer(), nullable=False),
        sa.Column('movieID', sa.Integer(), nullable=False),
        sa.Column('watched_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['movieID'], ['movies.movieID'], ),
        sa.ForeignKeyConstraint(['userID'], ['Users.UserId'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create read_history table
    op.create_table('read_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('userID', sa.Integer(), nullable=False),
        sa.Column('bookID', sa.Integer(), nullable=False),
        sa.Column('read_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bookID'], ['Books.BookId'], ),
        sa.ForeignKeyConstraint(['userID'], ['Users.UserId'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Reviews table if it doesn't exist
    op.create_table('Reviews',
        sa.Column('ReviewId', sa.Integer(), nullable=False),
        sa.Column('UserId', sa.Integer(), nullable=False),
        sa.Column('MovieAdaptationId', sa.Integer(), nullable=True),
        sa.Column('MovieId', sa.Integer(), nullable=True),
        sa.Column('Rating', sa.Integer(), nullable=True),
        sa.Column('Comment', sa.String(), nullable=True),
        sa.Column('CreatedAt', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['MovieAdaptationId'], ['MovieAdaptations.MovieAdaptationId'], ),
        sa.ForeignKeyConstraint(['MovieId'], ['movies.movieID'], ),
        sa.ForeignKeyConstraint(['UserId'], ['Users.UserId'], ),
        sa.PrimaryKeyConstraint('ReviewId')
    )

    # Add foreign key constraint to MovieAdaptations.movieID
    with op.batch_alter_table('MovieAdaptations') as batch_op:
        batch_op.create_foreign_key(
            'fk_movieadaptations_movies',
            'movies',
            ['movieID'],
            ['movieID']
        )

def downgrade():
    # Remove foreign key constraint from MovieAdaptations
    with op.batch_alter_table('MovieAdaptations') as batch_op:
        batch_op.drop_constraint('fk_movieadaptations_movies', type_='foreignkey')

    # Drop tables in reverse order
    op.drop_table('Reviews')
    op.drop_table('read_history')
    op.drop_table('watch_history')
    op.drop_table('watchlist')
    op.drop_table('movies')
