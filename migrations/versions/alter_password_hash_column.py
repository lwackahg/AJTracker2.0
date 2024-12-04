"""alter password_hash column size

Revision ID: alter_password_hash_column
Revises: 834157ecbf96
Create Date: 2024-11-24 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'alter_password_hash_column'
down_revision = '834157ecbf96'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                              existing_type=sa.String(length=128),
                              type_=sa.String(length=512),
                              existing_nullable=True)

def downgrade():
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
                              existing_type=sa.String(length=512),
                              type_=sa.String(length=128),
                              existing_nullable=True)
