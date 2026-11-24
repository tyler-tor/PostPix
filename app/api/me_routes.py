from flask import Blueprint, request
from flask_login import current_user, login_required
from sqlalchemy import select, or_
from app.models import db, Post
from app.models.user import follows
from app.api.serializers import page_of_posts
from app.api.pagination import get_limit, decode_time_cursor, bad_cursor

me_routes = Blueprint('me', __name__)


@me_routes.route('/following/posts')
@login_required
def me_following_posts():
    """Home feed: posts from everyone the current user follows, plus their own,
    newest first, one cursor page at a time (?limit=12&before=<cursor>).

    A fixed number of queries per page, no matter how many people you follow.
    """
    try:
        before = decode_time_cursor(request.args.get('before'))
    except ValueError:
        return bad_cursor()
    followed_ids = select(follows.c.followed_id).where(
        follows.c.follower_id == current_user.id)
    statement = (select(Post)
                 .where(or_(Post.user_id.in_(followed_ids), Post.user_id == current_user.id))
                 .order_by(Post.created_at.desc(), Post.id.desc()))
    return page_of_posts(statement, current_user.id, get_limit(12, 50), before)
