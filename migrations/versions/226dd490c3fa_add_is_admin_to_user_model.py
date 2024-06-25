"""Add is_admin to User model

Revision ID: 226dd490c3fa
Revises: 19a7b7496ff8
Create Date: 2023-06-24 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean

# revision identifiers, used by Alembic.
revision = '226dd490c3fa'
down_revision = '19a7b7496ff8'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    connection = op.get_bind()

    # Define table structure for old user table
    user_table = table(
        'user',
        column('id', Integer),
        column('username', String),
        column('email', String),
        column('image_file', String),
        column('password', String),
        column('is_admin', Boolean),
    )

    # Create new user table with the updated schema
    op.create_table(
        'new_user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(20), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('image_file', sa.String(100), nullable=False, server_default='default.jpg'),
        sa.Column('password', sa.String(60), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('0'))
    )

    # Copy data from old user table to new user table
    connection.execute(
        sa.text(
            """
            INSERT INTO new_user (id, username, email, image_file, password, is_admin)
            SELECT id, username, email, image_file, password, is_admin
            FROM user
            """
        )
    )

    # Drop old user table
    op.drop_table('user')

    # Rename new_user table to user
    op.rename_table('new_user', 'user')

def downgrade():
    connection = op.get_bind()

    # Create old user table with the previous schema
    op.create_table(
        'new_user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(20), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('image_file', sa.String(20), nullable=False, server_default='default.jpg'),
        sa.Column('password', sa.String(60), nullable=False)
    )

    # Copy data from current user table to new_user table
    connection.execute(
        sa.text(
            """
            INSERT INTO new_user (id, username, email, image_file, password)
            SELECT id, username, email, image_file, password
            FROM user
            """
        )
    )

    # Drop current user table
    op.drop_table('user')

    # Rename new_user table to user
    op.rename_table('new_user', 'user')
