from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, logout_user
from app.models import Post, User, Comment, PostLike, db
from app.forms.create_post import CreatePost
from app.forms.update_post import UpdatePost
from app.forms.create_comment import CreateComment
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.api.serializers import serialize_post, serialize_posts, page_of_posts
from app.api.pagination import get_limit, decode_time_cursor, encode_time_cursor, newer_than, bad_cursor



post_routes = Blueprint('posts', __name__)

def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{field} : {error}')
    return errorMessages

#get all posts (explore), newest first, one cursor page at a time
@post_routes.route('/')
@login_required
def posts():
    try:
        before = decode_time_cursor(request.args.get('before'))
    except ValueError:
        return bad_cursor()
    statement = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
    return page_of_posts(statement, current_user.id, get_limit(12, 50), before)

@post_routes.route('/<int(max=2147483647):id>', methods=['GET'])
@login_required
def get_post_by_id(id):
    post = db.get_or_404(Post, id, description='Post not found')
    return serialize_post(post, current_user.id)

@post_routes.route('/', methods=['POST'])
@login_required
def create_post():
    form = CreatePost()

    if form.validate_on_submit():
        post = Post(
            user_id=current_user.id,
            caption=form.data['caption'],
            img_url=form.data['img_url'],
            thumb_url=form.data['thumb_url'] or None,
            img_width=form.data['img_width'],
            img_height=form.data['img_height'],
        )
        db.session.add(post)
        db.session.commit()
        # Return the post we just created (not "the newest post in the table",
        # which could belong to someone else if two users post at once).
        return serialize_post(post, current_user.id)
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@post_routes.route('/<int(max=2147483647):id>', methods=['PUT'])
@login_required
def update_post(id):
    form = UpdatePost()
    post = db.session.get(Post, id)
    if not post:
        return {'errors': ['Post not found']}, 404
    # Only the author may edit a caption (prevents editing other users' posts by ID).
    if post.user_id != current_user.id:
        return {'errors': ['Forbidden']}, 403
    if form.validate_on_submit():
        post.caption = form.data['caption']
        db.session.commit()
        return serialize_post(post, current_user.id)
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@post_routes.route('/<int(max=2147483647):id>', methods=['DELETE'])
@login_required
def delete_post(id):
    post = db.session.get(Post, id)
    if not post:
        return {'errors': ['Post not found']}, 404
    if current_user.id != post.user_id:
        return {'errors': ['Forbidden']}, 403
    db.session.delete(post)
    db.session.commit()
    return {'message': 'Success'}


# Add post like endpoints here!


@post_routes.route('/<int(max=2147483647):id>/likes/users', methods=['GET'])
@login_required
def get_user_liked(id):
    '''
        get all users that liked a post
    '''
    db.get_or_404(Post, id, description='Post not found')
    after = request.args.get('after', type=int)
    limit = get_limit(30, 100)
    statement = (select(User, PostLike.id).join(PostLike, PostLike.user_id == User.id)
                 .where(PostLike.post_id == id).order_by(PostLike.id))
    if after:
        statement = statement.where(PostLike.id > after)
    rows = db.session.execute(statement.limit(limit + 1)).all()
    more = len(rows) > limit
    rows = rows[:limit]
    return {'user': [{'id': u.id, 'username': u.username,
                      'profilePicture': u.profile_picture} for u, _ in rows],
            'nextCursor': str(rows[-1][1]) if more else None}

@post_routes.route('/<int(max=2147483647):id>/likes', methods=['POST'])
@login_required
def like_post(id):
    '''
        current user like a post (once)
    '''
    post = db.get_or_404(Post, id, description='Post not found')
    already = db.session.scalar(select(PostLike).filter_by(user_id=current_user.id, post_id=id))
    if already:
        return {'errors': ['You already liked this post']}, 409
    db.session.add(PostLike(user_id=current_user.id, post_id=id))
    # Increment in SQL (likes = likes + 1) so two simultaneous likes can't
    # overwrite each other's count.
    db.session.execute(
        update(Post).where(Post.id == id)
        .values(likes=func.coalesce(Post.likes, 0) + 1)
        .execution_options(synchronize_session=False))
    try:
        db.session.commit()
    except IntegrityError:
        # Unique constraint hit by a racing duplicate request.
        db.session.rollback()
        return {'errors': ['You already liked this post']}, 409
    db.session.refresh(post)
    return {'likes': post.likes, 'postId': post.id, 'likedByMe': True}


@post_routes.route('/<int(max=2147483647):id>/likes', methods=['DELETE'])
@login_required
def unlike_post(id):
    '''
        current user unlike post
    '''
    post = db.get_or_404(Post, id, description='Post not found')
    like = db.session.scalar(select(PostLike).filter_by(user_id=current_user.id, post_id=id))
    if not like:
        return {'errors': ['You have not liked this post']}, 404
    db.session.delete(like)
    db.session.execute(
        update(Post).where(Post.id == id, Post.likes > 0)
        .values(likes=Post.likes - 1)
        .execution_options(synchronize_session=False))
    db.session.commit()
    # Re-read so we return the NEW count (the old code returned the stale one).
    db.session.refresh(post)
    return {'postId': post.id, 'likes': post.likes, 'likedByMe': False}


@post_routes.route('/<int(max=2147483647):id>/comments')
@login_required
def comments_on_post(id):
    """Comments of a post, oldest first, one cursor page at a time."""
    db.get_or_404(Post, id, description='Post not found')
    try:
        after = decode_time_cursor(request.args.get('after'))
    except ValueError:
        return bad_cursor()
    limit = get_limit(20, 100)
    statement = (select(Comment).where(Comment.post_id == id)
                 .options(db.joinedload(Comment.users))
                 .order_by(Comment.created_at, Comment.id))
    if after:
        statement = statement.where(newer_than(Comment.created_at, Comment.id, after))
    rows = db.session.scalars(statement.limit(limit + 1)).all()
    more = len(rows) > limit
    rows = rows[:limit]
    return {
        'Comments': [{**c.to_dict(),
                      'users': {'username': c.users.username, 'id': c.users.id,
                                'profilePicture': c.users.profile_picture},
                      'myComment': c.user_id == current_user.id} for c in rows],
        'nextCursor': encode_time_cursor(rows[-1].created_at, rows[-1].id) if more else None,
    }


@post_routes.route('/<int(max=2147483647):id>/comments', methods=['POST'])
@login_required
def create_comment_post(id):
    post = db.get_or_404(Post, id, description='Post not found')
    user = current_user
    form = CreateComment()
    if form.validate_on_submit():
        comment = Comment(
            user_id=current_user.id,
            body=form.data['body'],
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        comment_dict = comment.to_dict()
        #! added comment recogintion on the backend to make front end rendering easier.
        comment_dict['myComment'] = True;
        comment_dict['users'] = {
            'userId': user.id,
            'username': user.username,
            'profilePicture' : user.profile_picture
        }
        return comment_dict
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400
