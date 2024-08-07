"""empty message

Revision ID: 5c201fad79b6
Revises: 71918d9249b0
Create Date: 2024-06-30 16:20:12.685745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c201fad79b6'
down_revision = '71918d9249b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action_required',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tracking_number', sa.String(length=100), nullable=False),
    sa.Column('first_name', sa.String(length=80), nullable=False),
    sa.Column('last_name', sa.String(length=80), nullable=False),
    sa.Column('item_number', sa.String(length=20), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('sender', sa.String(length=100), nullable=True),
    sa.Column('date_received', sa.DateTime(), nullable=True),
    sa.Column('invoice', sa.String(length=255), nullable=True),
    sa.Column('reason', sa.String(length=255), nullable=False),
    sa.Column('action_needed', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item_number')
    )
    op.create_table('packages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tracking_number', sa.String(length=100), nullable=False),
    sa.Column('first_name', sa.String(length=80), nullable=False),
    sa.Column('last_name', sa.String(length=80), nullable=False),
    sa.Column('item_number', sa.String(length=20), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('sender', sa.String(length=100), nullable=True),
    sa.Column('date_received', sa.DateTime(), nullable=True),
    sa.Column('invoice', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('packages')
    op.drop_table('action_required')
    # ### end Alembic commands ###
