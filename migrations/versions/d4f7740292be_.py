"""empty message

Revision ID: d4f7740292be
Revises: update_json_storage
Create Date: 2024-11-28 12:37:13.150919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4f7740292be'
down_revision = 'update_json_storage'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('BookId', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'Books', ['BookId'], ['BookId'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Reviews', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('BookId')

    # ### end Alembic commands ###
