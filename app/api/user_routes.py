from flask import Blueprint, jsonify
from flask_login import login_required, current_user, logout_user
from flask import request
from sqlalchemy import select, delete, insert, func
from sqlalchemy.exc import IntegrityError
from app.api.serializers import page_of_posts
from app.api.pagination import decode_time_cursor, bad_cursor, get_limit
from app.models import User, db, Post, PostLike
from app.models.user import follows, user_summary

user_routes = Blueprint('users', __name__)

def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{field} : {error}')
    return errorMessages


def _limit(default, maximum=100):
    """?limit=N from the query string, clamped to 1..maximum."""
    try:
        value = int(request.args.get('limit', default))
    except ValueError:
        value = default
    return max(1, min(value, maximum))


def _stats_dicts(statement):
    return [User.row_to_dict(row) for row in db.session.execute(statement)]


@user_routes.route('/')
@login_required
def users():
    # Lightweight payloads (counts, no lists) and a cap, so this stays fast
    # as the number of users grows. Use /api/users/search to look people up.
    rows = _stats_dicts(User.stats_select(current_user.id)
                        .order_by(User.id).limit(_limit(50)))
    return {'users': rows}


@user_routes.route('/search')
@login_required
def search_users():
    """Find people by username prefix: /api/users/search?q=ab&limit=10.

    Case-insensitive. Written as a range on lower(username)
    (lower(username) >= 'ab' AND lower(username) < 'ac') so it uses the
    ix_users_username_lower index and needs no LIKE wildcard escaping.
    """
    q = request.args.get('q', '').strip().lower()[:40]
    if not q:
        return {'users': []}
    name = func.lower(User.username)
    statement = select(User).where(name >= q)
    if ord(q[-1]) < 0x10FFFF:  # the largest code point has no "next" character
        statement = statement.where(name < q[:-1] + chr(ord(q[-1]) + 1))
    users = db.session.scalars(statement.order_by(name).limit(_limit(10, 25))).all()
    return {'users': [user_summary(u) for u in users]}


@user_routes.route('/<int(max=2147483647):id>')
@login_required
def user(id):
    row = db.session.execute(
        User.stats_select(current_user.id).where(User.id == id)).first()
    if row is None:
        return {'errors': ['User not found']}, 404
    return User.row_to_dict(row)


@user_routes.route('/<int(max=2147483647):id>/posts')
@login_required
def user_posts(id):
    """One user's posts for the profile grid, newest first, one cursor page at a
    time (?limit=12&before=<cursor>)."""
    db.get_or_404(User, id, description='User not found')
    try:
        before = decode_time_cursor(request.args.get('before'))
    except ValueError:
        return bad_cursor()
    statement = (select(Post).where(Post.user_id == id)
                 .order_by(Post.created_at.desc(), Post.id.desc()))
    return page_of_posts(statement, current_user.id, get_limit(12, 50), before)


@user_routes.route('/<int(max=2147483647):id>', methods=['DELETE'])
@login_required
def delete_user(id):
    # Only the logged-in user may delete their own account.
    if current_user.id != id:
        return {'errors': ['You can only delete your own account']}, 403
    user = db.session.get(User, id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return {'message': 'Success'}

def _people_page(id, join_on, filter_on, key):
    """Followers / following of user <id>, ordered by user id, one cursor page
    at a time (?limit=30&after=<last user id>)."""
    db.get_or_404(User, id, description='User not found')
    after = request.args.get('after', type=int)
    limit = _limit(30)
    statement = (select(User).join(follows, join_on).where(filter_on == id).order_by(User.id))
    if after:
        statement = statement.where(User.id > after)
    rows = db.session.scalars(statement.limit(limit + 1)).all()
    more = len(rows) > limit
    rows = rows[:limit]
    return {key: [user_summary(u) for u in rows],
            'nextCursor': str(rows[-1].id) if more else None}


@user_routes.route('/<int(max=2147483647):id>/followers', methods=['GET'])
@login_required
def get_followers(id):
    """People who follow user <id> (summary shape: id, username, picture...)."""
    return _people_page(id, follows.c.follower_id == User.id, follows.c.followed_id, 'followers')


@user_routes.route('/<int(max=2147483647):id>/following', methods=['GET'])
@login_required
def get_following(id):
    """People user <id> follows."""
    return _people_page(id, follows.c.followed_id == User.id, follows.c.follower_id, 'following')


@user_routes.route('/<int(max=2147483647):id>/notfollowing', methods=['GET'])
@login_required
def get_not_following(id):
    """Suggestions: users that <id> does not follow yet (and not <id> itself).
    One query with NOT IN (subquery) and a LIMIT, instead of loading every user."""
    db.get_or_404(User, id, description='User not found')
    already = select(follows.c.followed_id).where(follows.c.follower_id == id)
    stmt = (User.stats_select(current_user.id)
            .where(User.id != id, User.id.notin_(already))
            .order_by(User.id).limit(_limit(10, 50)))
    return {'users': _stats_dicts(stmt)}


@user_routes.route('/<int(max=2147483647):id>/follow', methods=['POST'])
@login_required
def follow_user(id):
    f_user = db.session.get(User, id)
    if not f_user:
        return {'errors': ['User not found']}, 404
    try:
        db.session.execute(insert(follows).values(
            follower_id=current_user.id, followed_id=id))
        db.session.commit()
    except IntegrityError:
        # The unique (follower, followed) constraint caught a duplicate.
        db.session.rollback()
        return {'errors': ['You are already following this user']}, 409
    return {'currentUser': current_user.to_dict(), 'followingUser': f_user.to_dict()}


@user_routes.route('/<int(max=2147483647):id>/follow', methods=['DELETE'])
@login_required
def unfollow_user(id):
    f_user = db.session.get(User, id)
    if not f_user:
        return {'errors': ['User not found']}, 404
    result = db.session.execute(delete(follows).where(
        follows.c.follower_id == current_user.id, follows.c.followed_id == id))
    db.session.commit()
    if result.rowcount == 0:
        return {'errors': ['You are not following this user']}, 409
    return {'currentUser': current_user.to_dict(), 'followingUser': f_user.to_dict()}

@user_routes.route('/<int(max=2147483647):id>/likes', methods=['GET'])
@login_required
def get_all_liked_posts(id):
    db.get_or_404(User, id, description='User not found')
    posts = db.session.scalars(
        select(Post).join(PostLike, PostLike.post_id == Post.id)
        .where(PostLike.user_id == id).order_by(Post.id)).all()
    return {'likedPosts': [post.to_dict() for post in posts]}


@user_routes.route('/likes')
@login_required
def get_posts_liked():
    """Posts the current user liked, with each post's like count (one query)."""
    rows = db.session.execute(
        select(PostLike.post_id, Post.likes)
        .join(Post, Post.id == PostLike.post_id)
        .where(PostLike.user_id == current_user.id)).all()
    return {'likes': [{'postId': post_id, 'likes': likes} for post_id, likes in rows]}
