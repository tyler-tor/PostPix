"""index for case-insensitive username search (P23)

Revision ID: 0003_user_search
Revises: 0002_indexes
Create Date: 2026-11-24 10:00:00

GET /api/users/search matches lower(username) against a range
(lower(username) >= 'ab' AND lower(username) < 'ac'). This expression index
lets both SQLite and Postgres answer that without scanning the users table.
"""
from alembic import op
import sqlalchemy as sa


revision = '0003_user_search'
down_revision = '0002_indexes'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_users_username_lower', 'users', [sa.text('lower(username)')])


def downgrade():
    op.drop_index('ix_users_username_lower', table_name='users')
