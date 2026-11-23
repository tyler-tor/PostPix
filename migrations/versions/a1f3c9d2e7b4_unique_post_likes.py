"""P6: one like per user per post; recount posts.likes

Revision ID: a1f3c9d2e7b4
Revises: e66be29cbd54
Create Date: 2026-11-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1f3c9d2e7b4'
down_revision = 'e66be29cbd54'
branch_labels = None
depends_on = None

# In production, env.py sets the Postgres search_path to SCHEMA, so the
# unqualified table names below resolve to the right schema.


def upgrade():
    # 1. Remove duplicate likes (keep the oldest row of each user/post pair),
    #    otherwise the unique constraint cannot be created.
    op.execute(
        'DELETE FROM post_likes WHERE id NOT IN '
        '(SELECT MIN(id) FROM post_likes GROUP BY user_id, post_id)'
    )
    # 2. Add the unique constraint. batch_alter_table makes this work on
    #    SQLite too (it rebuilds the table there; plain ALTER on Postgres).
    with op.batch_alter_table('post_likes') as batch_op:
        batch_op.create_unique_constraint(
            'uq_post_likes_user_post', ['user_id', 'post_id'])
    # 3. Make the denormalized counter match the real rows.
    op.execute(
        'UPDATE posts SET likes = '
        '(SELECT COUNT(*) FROM post_likes WHERE post_likes.post_id = posts.id)'
    )


def downgrade():
    with op.batch_alter_table('post_likes') as batch_op:
        batch_op.drop_constraint('uq_post_likes_user_post', type_='unique')
