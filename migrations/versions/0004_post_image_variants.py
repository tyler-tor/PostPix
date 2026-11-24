"""posts: thumbnail URL and image size (P24)

Revision ID: 0004_post_images
Revises: 0003_user_search
Create Date: 2026-11-24 11:00:00

New uploads are resized (see app/s3_helpers.py): img_url is the 1080 px WebP,
thumb_url a 400 px WebP for grids, img_width / img_height the size of img_url
so pages can reserve the space and avoid layout jumps. All nullable: older
posts and the seed data use external pictures and have none of them.
"""
from alembic import op
import sqlalchemy as sa


revision = '0004_post_images'
down_revision = '0003_user_search'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('posts') as batch:
        batch.add_column(sa.Column('thumb_url', sa.String(length=255), nullable=True))
        batch.add_column(sa.Column('img_width', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('img_height', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('posts') as batch:
        batch.drop_column('img_height')
        batch.drop_column('img_width')
        batch.drop_column('thumb_url')
