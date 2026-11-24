"""indexes on the columns the app filters by; ON DELETE CASCADE on follows (P21)

Revision ID: 0002_indexes
Revises: 0001_baseline
Create Date: 2026-11-24 09:00:00

Postgres does not index foreign keys automatically, so feeds, profile pages,
comment lists and like lists would scan whole tables as data grows.

  posts(user_id, created_at)        profile page: one user's posts, newest first
  posts(created_at, id)             explore / home feed ordering and cursor paging
  comments(post_id)                 comments of one post
  post_likes(post_id)               likes of one post
  follows(followed_id)              "who follows X" (the unique constraint only
                                    covers lookups that start with follower_id)

The two posts indexes are plain ascending: the databases scan an index backwards
for ORDER BY ... DESC, so a DESC index adds nothing.

The follows foreign keys also get ON DELETE CASCADE, so deleting a user removes
their follow rows in the database itself.
"""
from alembic import op
import sqlalchemy as sa


revision = '0002_indexes'
down_revision = '0001_baseline'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_posts_user_id_created_at', 'posts', ['user_id', 'created_at'])
    op.create_index('ix_posts_created_at_id', 'posts', ['created_at', 'id'])
    op.create_index('ix_comments_post_id', 'comments', ['post_id'])
    op.create_index('ix_post_likes_post_id', 'post_likes', ['post_id'])
    op.create_index('ix_follows_followed_id', 'follows', ['followed_id'])

    # batch mode = ALTER on Postgres, "copy the table" on SQLite (which cannot
    # alter foreign keys in place).
    with op.batch_alter_table('follows') as batch:
        batch.drop_constraint('fk_follows_followed_id_users', type_='foreignkey')
        batch.drop_constraint('fk_follows_follower_id_users', type_='foreignkey')
        batch.create_foreign_key('fk_follows_followed_id_users', 'users', ['followed_id'], ['id'], ondelete='CASCADE')
        batch.create_foreign_key('fk_follows_follower_id_users', 'users', ['follower_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('follows') as batch:
        batch.drop_constraint('fk_follows_followed_id_users', type_='foreignkey')
        batch.drop_constraint('fk_follows_follower_id_users', type_='foreignkey')
        batch.create_foreign_key('fk_follows_followed_id_users', 'users', ['followed_id'], ['id'])
        batch.create_foreign_key('fk_follows_follower_id_users', 'users', ['follower_id'], ['id'])

    op.drop_index('ix_follows_followed_id', table_name='follows')
    op.drop_index('ix_post_likes_post_id', table_name='post_likes')
    op.drop_index('ix_comments_post_id', table_name='comments')
    op.drop_index('ix_posts_created_at_id', table_name='posts')
    op.drop_index('ix_posts_user_id_created_at', table_name='posts')
