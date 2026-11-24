"""`flask demo reset`: put the shared demo account back to the seed data (P41).

Every visitor can click "Demo Login", so the demo account collects whatever
people do with it. A nightly job (cron or a systemd timer on the EC2) runs `flask demo reset`, which restores ONLY the demo user's
part of the database:

  * the demo user row itself (recreated if it is missing; name and picture restored)
  * the demo user's posts: exactly the seed posts (extra posts are deleted,
    deleted or edited seed posts come back), and on those posts exactly the
    seed comments and likes
  * comments and likes the demo user wrote on other people's posts
  * who the demo user follows and who follows the demo user

Other users' own posts, comments, likes and follows between other users are
never touched (the only side effect on them: like counters of posts whose
demo like was added/removed are recounted, and other people's comments or
likes ON the demo user's posts are reset with those posts).

It is safe in production: nothing is deleted outside the list above, it all
happens in one transaction, and running it twice in a row changes nothing the
second time (idempotent).

How "the seed data" is known without copying it: the regular seed functions
run against a throwaway in-memory SQLite database, and the demo user's part
is read from there by natural keys (emails, captions, comment text), never by
database ids, which differ between databases.
"""
import time
from collections import Counter
from datetime import datetime, timezone

import click
from flask import Flask, current_app
from flask.cli import AppGroup
from sqlalchemy import delete, func, insert, select, update

from app.models import Comment, Post, PostLike, User, db
from app.models.user import DEMO_EMAIL, follows

demo_commands = AppGroup('demo', help='Tools for the shared demo account.')


# ---------------------------------------------------------------------------
# 1. What the seed says the demo account looks like
# ---------------------------------------------------------------------------
def seed_snapshot():
    """Return the demo user's seed state as plain data (no ids).

    {
      'profile':   {username, email, first_name, last_name, profile_picture, hashed_password},
      'posts':     [{'img_url', 'caption', 'comments': [(author_email, body)], 'likes': [email]}],
      'comments':  [(post_owner_email, post_caption, body)],  # on other users' posts
      'likes':     [(post_owner_email, post_caption)],         # on other users' posts
      'following': [email], 'followers': [email],
    }
    """
    from app.seeds import _seed  # local import: app.seeds imports this module

    scratch = Flask('postpix-seed-snapshot')
    scratch.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite://',  # in memory, gone afterwards
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Same image URLs as the real app would seed right now.
        MEDIA_BASE_URL=current_app.config.get('MEDIA_BASE_URL', ''),
    )
    db.init_app(scratch)
    with scratch.app_context():
        try:
            db.create_all()
            _seed()
            return _describe_demo(db.session.scalar(select(User).where(User.email == DEMO_EMAIL)))
        finally:
            db.session.remove()
            db.engine.dispose()


def _describe_demo(demo):
    email_of = dict(db.session.execute(select(User.id, User.email)).all())
    posts = db.session.scalars(select(Post).order_by(Post.id)).all()
    post_key = {p.id: (email_of[p.user_id], p.caption) for p in posts}

    own_posts = []
    for post in posts:
        if post.user_id != demo.id:
            continue
        comments = db.session.execute(
            select(Comment.user_id, Comment.body).where(Comment.post_id == post.id)
            .order_by(Comment.id)).all()
        likers = db.session.scalars(select(PostLike.user_id).where(PostLike.post_id == post.id)).all()
        own_posts.append({
            'img_url': post.img_url,
            'caption': post.caption,
            'comments': [(email_of[uid], body) for uid, body in comments],
            'likes': sorted(email_of[uid] for uid in likers),
        })

    elsewhere = select(Post.id).where(Post.user_id != demo.id)
    comments = db.session.execute(
        select(Comment.post_id, Comment.body)
        .where(Comment.user_id == demo.id, Comment.post_id.in_(elsewhere))
        .order_by(Comment.id)).all()
    likes = db.session.scalars(
        select(PostLike.post_id)
        .where(PostLike.user_id == demo.id, PostLike.post_id.in_(elsewhere))).all()
    following = db.session.scalars(
        select(follows.c.followed_id).where(follows.c.follower_id == demo.id)).all()
    followers = db.session.scalars(
        select(follows.c.follower_id).where(follows.c.followed_id == demo.id)).all()

    return {
        'profile': {
            'username': demo.username, 'email': demo.email,
            'first_name': demo.first_name, 'last_name': demo.last_name,
            'profile_picture': demo.profile_picture, 'hashed_password': demo.hashed_password,
        },
        'posts': own_posts,
        'comments': [(*post_key[pid], body) for pid, body in comments],
        'likes': sorted(post_key[pid] for pid in likes),
        'following': sorted(email_of[uid] for uid in following),
        'followers': sorted(email_of[uid] for uid in followers),
    }


# ---------------------------------------------------------------------------
# 2. Make the live database match it
# ---------------------------------------------------------------------------
class DemoResetError(click.ClickException):
    pass


def reset_demo(snapshot=None):
    """Bring the demo user's data back to the seed. Does NOT commit.

    Returns a Counter of what changed (empty = it already matched).
    The caller commits (or rolls back for a dry run).
    """
    snapshot = snapshot or seed_snapshot()
    changes = Counter()

    if db.session.scalar(select(func.count()).select_from(User)) == 0:
        raise DemoResetError(
            'The database has no users. Run `flask seed all` first; '
            '`flask demo reset` only repairs the demo account of a seeded database.')

    profile = snapshot['profile']
    # Row lock on Postgres, so two resets (or a reset and a demo request that
    # deletes the account) cannot interleave. SQLite ignores it.
    demo = db.session.scalar(
        select(User).where(User.email == DEMO_EMAIL).with_for_update())
    if demo is None:
        _check_username_free(profile['username'], None)
        demo = User(email=DEMO_EMAIL, username=profile['username'],
                    first_name=profile['first_name'], last_name=profile['last_name'],
                    profile_picture=profile['profile_picture'])
        demo.hashed_password = profile['hashed_password']
        db.session.add(demo)
        db.session.flush()
        changes['demo user recreated'] += 1
    else:
        for field in ('username', 'first_name', 'last_name', 'profile_picture'):
            if getattr(demo, field) != profile[field]:
                if field == 'username':
                    _check_username_free(profile['username'], demo.id)
                setattr(demo, field, profile[field])
                changes['profile fields restored'] += 1

    # Seed users other than the demo user, by email (only those that still exist).
    emails = ({e for p in snapshot['posts'] for e, _ in p['comments']}
              | {e for p in snapshot['posts'] for e in p['likes']}
              | {e for e, _, _ in snapshot['comments']} | {e for e, _ in snapshot['likes']}
              | set(snapshot['following']) | set(snapshot['followers']))
    user_id = dict(db.session.execute(
        select(User.email, User.id).where(User.email.in_(emails))).all())
    user_id[DEMO_EMAIL] = demo.id
    touched_posts = set()

    # -- the demo user's own posts -----------------------------------------
    unclaimed = list(db.session.scalars(
        select(Post).where(Post.user_id == demo.id).order_by(Post.id)))
    kept = []
    for spec in snapshot['posts']:
        post = next((p for p in unclaimed
                     if p.img_url == spec['img_url'] and p.caption == spec['caption']), None)
        if post is not None:
            unclaimed.remove(post)
        else:
            post = Post(user_id=demo.id, img_url=spec['img_url'], caption=spec['caption'], likes=0)
            db.session.add(post)
            db.session.flush()
            changes['posts restored'] += 1
        kept.append((post, spec))
    for post in unclaimed:
        # ORM delete: the post's comments and likes go with it (cascade).
        db.session.delete(post)
        changes['posts removed'] += 1
    db.session.flush()

    for post, spec in kept:
        wanted_comments = [(user_id[e], body) for e, body in spec['comments'] if e in user_id]
        existing = db.session.scalars(select(Comment).where(Comment.post_id == post.id)
                                      .order_by(Comment.id)).all()
        _sync_comments(existing, wanted_comments, key=lambda c: (c.user_id, c.body),
                       make=lambda uid, body, pid=post.id: Comment(user_id=uid, post_id=pid, body=body),
                       changes=changes, label='comments on demo posts')
        wanted_likers = {user_id[e] for e in spec['likes'] if e in user_id}
        _sync_likes_on_post(post.id, wanted_likers, changes)
        touched_posts.add(post.id)

    # -- what the demo user wrote / liked on other people's posts ------------
    def find_post(owner_email, caption):
        owner = user_id.get(owner_email)
        if owner is None or owner == demo.id:
            return None
        return db.session.scalar(select(Post.id).where(Post.user_id == owner, Post.caption == caption)
                                 .order_by(Post.id).limit(1))

    wanted = []
    for owner_email, caption, body in snapshot['comments']:
        pid = find_post(owner_email, caption)
        if pid is not None:
            wanted.append((pid, body))
    existing = db.session.scalars(
        select(Comment).join(Post, Comment.post_id == Post.id)
        .where(Comment.user_id == demo.id, Post.user_id != demo.id).order_by(Comment.id)).all()
    _sync_comments(existing, wanted, key=lambda c: (c.post_id, c.body),
                   make=lambda pid, body: Comment(user_id=demo.id, post_id=pid, body=body),
                   changes=changes, label="demo's comments elsewhere")

    wanted_likes = {pid for pid in (find_post(o, c) for o, c in snapshot['likes']) if pid is not None}
    current_likes = set(db.session.scalars(
        select(PostLike.post_id).join(Post, PostLike.post_id == Post.id)
        .where(PostLike.user_id == demo.id, Post.user_id != demo.id)))
    for pid in current_likes - wanted_likes:
        db.session.execute(delete(PostLike).where(PostLike.user_id == demo.id, PostLike.post_id == pid))
        changes["demo's likes removed"] += 1
    for pid in wanted_likes - current_likes:
        db.session.add(PostLike(user_id=demo.id, post_id=pid))
        changes["demo's likes restored"] += 1
    touched_posts |= current_likes ^ wanted_likes

    # -- follows -------------------------------------------------------------
    _sync_follows(demo.id, 'follower_id', 'followed_id',
                  {user_id[e] for e in snapshot['following'] if e in user_id}, changes, 'following')
    _sync_follows(demo.id, 'followed_id', 'follower_id',
                  {user_id[e] for e in snapshot['followers'] if e in user_id}, changes, 'followers')

    # -- like counters of every post whose likes may have changed -----------
    db.session.flush()
    if touched_posts:
        real_count = (select(func.count(PostLike.id)).where(PostLike.post_id == Post.id)
                      .scalar_subquery())
        db.session.execute(update(Post).where(Post.id.in_(touched_posts)).values(likes=real_count)
                           .execution_options(synchronize_session=False))
    db.session.expire_all()
    return changes


def _check_username_free(username, demo_id):
    other = db.session.scalar(select(User.id).where(User.username == username))
    if other is not None and other != demo_id:
        raise DemoResetError(
            f'Another account (id {other}) uses the demo username {username!r}; '
            'rename it before resetting the demo account.')


def _sync_comments(existing, wanted, key, make, changes, label):
    """Make the `existing` comments equal the multiset `wanted` of (a, body)
    pairs: keep matches, delete the rest, add what is missing with make(a, body)."""
    need = Counter(wanted)
    for comment in existing:
        k = key(comment)
        if need[k] > 0:
            need[k] -= 1
        else:
            db.session.delete(comment)
            changes[f'{label} removed'] += 1
    for (a, body), count in need.items():
        for _ in range(count):
            db.session.add(make(a, body))
            changes[f'{label} restored'] += 1


def _sync_likes_on_post(post_id, wanted_user_ids, changes):
    current = set(db.session.scalars(select(PostLike.user_id).where(PostLike.post_id == post_id)))
    for uid in current - wanted_user_ids:
        db.session.execute(delete(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == uid))
        changes['likes on demo posts removed'] += 1
    for uid in wanted_user_ids - current:
        db.session.add(PostLike(user_id=uid, post_id=post_id))
        changes['likes on demo posts restored'] += 1


def _sync_follows(demo_id, demo_column, other_column, wanted, changes, label):
    demo_col, other_col = follows.c[demo_column], follows.c[other_column]
    current = set(db.session.scalars(select(other_col).where(demo_col == demo_id)))
    for uid in current - wanted:
        db.session.execute(delete(follows).where(demo_col == demo_id, other_col == uid))
        changes[f'{label} removed'] += 1
    for uid in wanted - current:
        db.session.execute(insert(follows).values({demo_column: demo_id, other_column: uid}))
        changes[f'{label} restored'] += 1


# ---------------------------------------------------------------------------
# 3. The command
# ---------------------------------------------------------------------------
@demo_commands.command('reset')
@click.option('--dry-run', is_flag=True,
              help='Show what would change, then roll back (nothing is saved).')
def reset_command(dry_run):
    """Restore the demo user's posts, comments, likes and follows to the seed data.

    Safe in production and safe to repeat: other users' data is not touched.
    """
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        changes = reset_demo()
        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    took = time.monotonic() - started
    prefix = f'[{stamp}] demo reset{" (dry run, nothing saved)" if dry_run else ""}:'
    if not changes:
        click.echo(f'{prefix} already matches the seed data ({took:.1f}s).')
        return
    summary = ', '.join(f'{name} {count}' for name, count in sorted(changes.items()))
    click.echo(f'{prefix} {summary} ({took:.1f}s).')
