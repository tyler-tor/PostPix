"""Shared JSON shapes for posts.

serialize_posts() turns a list of Post rows into API dicts for the logged-in
viewer with a fixed number of queries (not one per post):

  * the post columns            (already loaded)
  * "users": the author          (batch-loaded with selectinload by the caller)
  * "likedByMe": did the viewer like it?   -> 1 query for the whole list
  * "commentCount"                          -> 1 grouped query for the whole list

So the frontend never has to ask "which posts have I liked?" separately.
"""
from sqlalchemy import func, select
from app.models import Comment, PostLike, db


def author_dict(user):
    return {'userId': user.id, 'username': user.username,
            'profilePicture': user.profile_picture}


def serialize_posts(posts, viewer_id):
    posts = list(posts)
    ids = [p.id for p in posts]
    liked, counts = set(), {}
    if ids:
        liked = set(db.session.scalars(
            select(PostLike.post_id).where(PostLike.user_id == viewer_id,
                                           PostLike.post_id.in_(ids))))
        counts = dict(db.session.execute(
            select(Comment.post_id, func.count())
            .where(Comment.post_id.in_(ids)).group_by(Comment.post_id)).all())
    return [{**p.to_dict(),
             'likedByMe': p.id in liked,
             'commentCount': counts.get(p.id, 0),
             'users': author_dict(p.users)} for p in posts]


def serialize_post(post, viewer_id):
    return serialize_posts([post], viewer_id)[0]


def page_of_posts(statement, viewer_id, limit, before):
    """Run a posts SELECT (already filtered and ordered newest first) as one
    cursor page. Returns {'Posts': [...], 'nextCursor': str | None}."""
    from sqlalchemy.orm import selectinload
    from app.api.pagination import older_than, encode_time_cursor
    from app.models import Post
    if before:
        statement = statement.where(older_than(Post.created_at, Post.id, before))
    rows = db.session.scalars(
        statement.options(selectinload(Post.users)).limit(limit + 1)).all()
    more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_time_cursor(rows[-1].created_at, rows[-1].id) if more else None
    return {'Posts': serialize_posts(rows, viewer_id), 'nextCursor': next_cursor}
