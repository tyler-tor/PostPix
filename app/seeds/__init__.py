"""`flask seed ...` commands.

Rules (see CHANGES.md, P0):
- `flask seed all` is SAFE to run on every deploy: it only seeds an EMPTY
  database (no users) and otherwise does nothing.
- `flask seed all --reset` and `flask seed undo` DELETE all data. They are for
  local development only and refuse to run in production.
"""
import os

import click
from flask.cli import AppGroup
from sqlalchemy import delete, func, select

from app.models import db, User, Post, Comment, PostLike
from app.models.user import follows
from .users import seed_users
from .posts import seed_posts
from .comments import seed_comments
from .postLikes import seed_post_likes

# Creates a seed group to hold our commands
# So we can type `flask seed --help`
seed_commands = AppGroup('seed')


def _is_production():
    return os.environ.get('FLASK_ENV') == 'production'


def _refuse_in_production(command):
    if _is_production():
        raise click.ClickException(
            f'`{command}` deletes all data and is disabled in production. '
            'Restore from a backup instead, or run it against a local database.')


def _has_data():
    return db.session.scalar(select(func.count()).select_from(User)) > 0


def _delete_all():
    """Delete every row, children before parents, so foreign keys never break."""
    db.session.execute(delete(PostLike))
    db.session.execute(delete(Comment))
    db.session.execute(delete(follows))
    db.session.execute(delete(Post))
    db.session.execute(delete(User))
    db.session.commit()


def _seed():
    users = seed_users()
    posts = seed_posts(users)
    seed_comments(users, posts)
    seed_post_likes(users, posts)
    # Add other seed functions here


# Creates the `flask seed all` command
@seed_commands.command('all')
@click.option('--reset', is_flag=True,
              help='Delete ALL existing data first, then seed (local development only).')
def seed(reset):
    """Seed demo data into an empty database (safe to run on every deploy)."""
    if reset:
        _refuse_in_production('flask seed all --reset')
        _delete_all()
        click.echo('Deleted all existing data.')
    elif _has_data():
        click.echo('Database already has data. Skipping seed.')
        return
    _seed()
    click.echo('Seeded demo data.')


# Creates the `flask seed undo` command
@seed_commands.command('undo')
def undo():
    """Delete ALL data (local development only)."""
    _refuse_in_production('flask seed undo')
    _delete_all()
    click.echo('Deleted all data.')
