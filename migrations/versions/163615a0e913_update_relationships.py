"""update relationships

Revision ID: 163615a0e913
Revises: 834157ecbf96
Create Date: 2024-11-24 15:30:32.555830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '163615a0e913'
down_revision = '834157ecbf96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Books', schema=None) as batch_op:
        batch_op.alter_column('Title',
               existing_type=sa.NVARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=True,
               existing_server_default=sa.text("(N'')"))

    with op.batch_alter_table('MovieAdaptations', schema=None) as batch_op:
        batch_op.alter_column('BookId',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('((0))'))

    with op.batch_alter_table('Reviews', schema=None) as batch_op:
        batch_op.alter_column('UserId',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('Rating',
               existing_type=sa.FLOAT(precision=53),
               nullable=True)

    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.alter_column('Username',
               existing_type=sa.NVARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=True,
               existing_server_default=sa.text("(N'')"))
        batch_op.alter_column('Email',
               existing_type=sa.NVARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=True,
               existing_server_default=sa.text("(N'')"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.alter_column('Email',
               existing_type=sa.NVARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=False,
               existing_server_default=sa.text("(N'')"))
        batch_op.alter_column('Username',
               existing_type=sa.NVARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=False,
               existing_server_default=sa.text("(N'')"))

    with op.batch_alter_table('Reviews', schema=None) as batch_op:
        batch_op.alter_column('Rating',
               existing_type=sa.FLOAT(precision=53),
               nullable=False)
        batch_op.alter_column('UserId',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('MovieAdaptations', schema=None) as batch_op:
        batch_op.alter_column('BookId',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('((0))'))

    with op.batch_alter_table('Books', schema=None) as batch_op:
        batch_op.alter_column('Title',
               existing_type=sa.NVARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=False,
               existing_server_default=sa.text("(N'')"))

    # ### end Alembic commands ###
