"""empty message

Revision ID: 7d4b2b0c5749
Revises: 163615a0e913, alter_password_hash_column
Create Date: 2024-11-24 16:18:05.936137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d4b2b0c5749'
down_revision = ('163615a0e913', 'alter_password_hash_column')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
