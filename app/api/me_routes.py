from flask import Blueprint
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload
from app.models import db, Post
from app.models.user import follows

me_routes = Blueprint('me', __name__)


@me_routes.route('/following/posts')
@login_required
def me_following_posts():
    """Home feed: posts from everyone the current user follows, newest first.

    One query for the posts (plus one batched query for their authors via
    selectinload), instead of 1 query per followed user, and the result is
    sorted by time across all users instead of grouped by user.
    """
    followed_ids = db.session.query(follows.c.followed_id).filter(
        follows.c.follower_id == current_user.id)
    posts = (Post.query
             .filter(Post.user_id.in_(followed_ids))
             .options(selectinload(Post.users))
             .order_by(Post.created_at.desc(), Post.id.desc())
             .all())
    return {'Posts': [{**post.to_dict(), 'users': {
        'username': post.users.username,
        'profilePicture': post.users.profile_picture,
        'userId': post.users.id
    }} for post in posts]}
