"""Add user_id to Post model

Revision ID: 19a7b7496ff8
Revises: eb38bf3000fe
Create Date: 2024-06-24 18:27:04.153474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19a7b7496ff8'
down_revision = 'eb38bf3000fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'profile_pic')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_pic', sa.VARCHAR(length=20), nullable=True))
    # ### end Alembic commands ###