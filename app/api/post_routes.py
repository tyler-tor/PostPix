from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, logout_user
from app.models import Post, User, Comment, PostLike, db
from app.forms.create_post import CreatePost
from app.forms.update_post import UpdatePost
from app.forms.create_comment import CreateComment
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError



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

#get all posts
@post_routes.route('/')
@login_required
def posts():
    posts = db.session.scalars(
        select(Post)
        .options(db.joinedload(Post.users))
        .order_by(Post.created_at.desc(), Post.id.desc())
    ).all()
    posts_dict = {}
    posts_dict["Posts"] = [{**post.to_dict(), 'users': {
        'username': post.users.username, 'profilePicture': post.users.profile_picture,
        'userId': post.users.id}} for post in posts]
    return posts_dict

@post_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_post_by_id(id):
    post = db.get_or_404(Post, id, description='Post not found')
    post_dict = post.to_dict()
    user = post.users
    post_dict['users'] = {
        'profilePicture' : user.profile_picture,
        'userId' : user.id,
        'username' : user.username
    }
    return post_dict

@post_routes.route('/', methods=['POST'])
@login_required
def create_post():
    form = CreatePost()

    if form.validate_on_submit():
        post = Post(
            user_id=current_user.id,
            caption=form.data['caption'],
            img_url= form.data['img_url']
        )
        db.session.add(post)
        db.session.commit()
        # Return the post we just created (not "the newest post in the table",
        # which could belong to someone else if two users post at once).
        post_dict = post.to_dict()
        user = post.users
        post_dict['users'] = {
            'profilePicture' : user.profile_picture,
            'userId' : user.id,
            'username' : user.username
        }
        return post_dict
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@post_routes.route('/<int:id>', methods=['PUT'])
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
        user = db.session.get(User, post.user_id)
        post.caption = form.data['caption']
        db.session.commit()
        post_dict = post.to_dict()
        #! updated code to match the return from the other post routes. needed to include the associated user.
        post_dict['users'] = {
            'profilePicture' : user.profile_picture,
            'userId' : user.id,
            'username' : user.username
        }
        return post_dict
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@post_routes.route('/<int:id>', methods=['DELETE'])
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


@post_routes.route('/<int:id>/likes/users', methods=['GET'])
@login_required
def get_user_liked(id):
    '''
        get all users that liked a post
    '''
    db.get_or_404(Post, id, description='Post not found')
    users = db.session.scalars(
        select(User).join(PostLike, PostLike.user_id == User.id)
        .where(PostLike.post_id == id).order_by(PostLike.id)).all()
    return {'user': [{'id': u.id, 'username': u.username,
                      'profilePicture': u.profile_picture} for u in users]}

@post_routes.route('/<int:id>/likes', methods=['POST'])
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
    return {'likes': post.likes, 'postId': post.id}


@post_routes.route('/<int:id>/likes', methods=['DELETE'])
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
    return {'postId': post.id, 'likes': post.likes}


@post_routes.route('/<int:id>/comments')
@login_required
def comments_on_post(id):
    post = db.session.get(Post, id)
    if post:
        comments = db.session.scalars(
            select(Comment).where(Comment.post_id == post.id)
            .options(db.joinedload(Comment.users))
        ).all()
        # print(comments)
        comments_dict = {}
        comments_dict["Comments"] = [{**comment.to_dict(), 'users': {
            'username': comment.users.username, 'id': comment.users.id, 'profilePicture' : comment.users.profile_picture
            }} for comment in comments]
        for comment in comments_dict['Comments']:
            comment['myComment'] = False
            if comment['userId'] == current_user.id:
                comment['myComment'] = True

        return comments_dict
    return {'errors': ['Post not found']}, 404


@post_routes.route('/<int:id>/comments', methods=['POST'])
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
