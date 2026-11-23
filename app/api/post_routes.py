from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, logout_user
from app.models import Post, User, db, PostLike
from app.models import Post, User, Comment, db
from app.forms.create_post import CreatePost
from app.forms.update_post import UpdatePost
from app.forms.create_comment import CreateComment
from sqlalchemy import func
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
    posts = Post.query.options(db.joinedload(Post.users)).order_by(Post.created_at.desc()).all()
    posts_dict = {}
    posts_dict["Posts"] = [{**post.to_dict(), 'users': {
        'username': post.users.username, 'profilePicture': post.users.profile_picture,
        'userId': post.users.id}} for post in posts]
    return posts_dict

@post_routes.route('/<int:id>', methods=['GET'])
@login_required
def get_post_by_id(id):
    post = Post.query.get_or_404(id, description='Post not found')
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
    post = Post.query.get(id)
    if not post:
        return {'errors': ['Post not found']}, 404
    # Only the author may edit a caption (prevents editing other users' posts by ID).
    if post.user_id != current_user.id:
        return {'errors': ['Forbidden']}, 403
    if form.validate_on_submit():
        user = User.query.get(post.user_id)
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
    post = Post.query.get(id)
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
    post = Post.query.get(id)
    if(post):
        post_user_liked_arr = [post_like.users.to_dict() for post_like in post.post_likes]
        # print('DEBUG IN POSTLIKES --------------------------------------------', post_user_liked_arr)
        post_user_dict = {'user' : []}
        for user in post_user_liked_arr:
            post_user_dict['user'].append({'id':user['id'], 'username':user['username'], 'profilePicture':user['profilePicture']})
            # print(user)
        return post_user_dict
    return {'errors': ['Post not found']}, 404

@post_routes.route('/<int:id>/likes', methods=['POST'])
@login_required
def like_post(id):
    '''
        current user like a post (once)
    '''
    post = Post.query.get_or_404(id, description='Post not found')
    already = PostLike.query.filter_by(user_id=current_user.id, post_id=id).first()
    if already:
        return {'errors': ['You already liked this post']}, 409
    db.session.add(PostLike(user_id=current_user.id, post_id=id))
    # Increment in SQL (likes = likes + 1) so two simultaneous likes can't
    # overwrite each other's count.
    Post.query.filter_by(id=id).update({Post.likes: func.coalesce(Post.likes, 0) + 1},
                                       synchronize_session=False)
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
    post = Post.query.get_or_404(id, description='Post not found')
    like = PostLike.query.filter_by(user_id=current_user.id, post_id=id).first()
    if not like:
        return {'errors': ['You have not liked this post']}, 404
    db.session.delete(like)
    Post.query.filter(Post.id == id, Post.likes > 0).update(
        {Post.likes: Post.likes - 1}, synchronize_session=False)
    db.session.commit()
    # Re-read so we return the NEW count (the old code returned the stale one).
    db.session.refresh(post)
    return {'postId': post.id, 'likes': post.likes}


@post_routes.route('/<int:id>/comments')
@login_required
def comments_on_post(id):
    post = Post.query.get(id)
    if post:
        comments = Comment.query.filter(Comment.post_id == post.id).options(db.joinedload(Comment.users)).all()
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
    post = Post.query.get_or_404(id, description='Post not found')
    user = User.query.get(current_user.id)
    form = CreateComment()
    user = user.to_dict()
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
            'userId': user['id'],
            'username': user['username'],
            'profilePicture' : user['profilePicture']
        }
        return comment_dict
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400
