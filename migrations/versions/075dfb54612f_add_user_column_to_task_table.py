"""Add user column to Task table

Revision ID: 075dfb54612f
Revises: 
Create Date: 2024-08-21 14:47:47.062503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '075dfb54612f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('checklist_item', sa.String(length=100), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('user', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('Tasks')
    op.drop_table('user')
    op.drop_table('Users')
    op.drop_table('task')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), nullable=True),
    sa.Column('checklist_item', sa.VARCHAR(length=100), nullable=True),
    sa.Column('due_date', sa.DATETIME(), nullable=True),
    sa.Column('completed', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user', sa.VARCHAR(length=20), nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), nullable=False),
    sa.Column('password', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user', sa.VARCHAR(length=20), nullable=False),
    sa.Column('password', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Tasks',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), nullable=True),
    sa.Column('checklist_item', sa.VARCHAR(length=100), nullable=True),
    sa.Column('due_date', sa.DATETIME(), nullable=True),
    sa.Column('completed', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('User')
    op.drop_table('Task')
    # ### end Alembic commands ###
