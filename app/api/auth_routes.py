from flask import Blueprint, jsonify, session, request
from app.models import User, db, Post
from app.forms import LoginForm
from app.forms import SignUpForm
from flask_login import current_user, login_user, logout_user, login_required
from app.s3_helpers import process_and_upload_image

auth_routes = Blueprint('auth', __name__)


def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{field} : {error}')
    return errorMessages


@auth_routes.route('/')
def authenticate():
    """
    Authenticates a user.
    """
    if current_user.is_authenticated:
        curr_user = current_user.to_dict()
        posts = Post.query.filter(Post.user_id == curr_user['id']).all()
        curr_user['Posts'] = [post.to_dict() for post in posts]
        return curr_user
    return {'errors': ['Unauthorized']}


@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Logs a user in
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Add the user to the session, we are logged in!
        user = User.query.filter(User.email == form.data['email']).first()
        login_user(user)
        # print('TEST------------------------------------', user.test)
        return user.to_dict()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@auth_routes.route('/logout', methods=['POST'])
def logout():
    """
    Logs a user out
    """
    logout_user()
    return {'message': 'User logged out'}


@auth_routes.route('/signup', methods=['POST'])
def sign_up():
    """
    Creates a new user and logs them in
    """
    form = SignUpForm()
    if form.validate_on_submit():
        # The optional profile picture is sent in the same multipart request as
        # the signup fields, because /api/img/upload now requires a logged-in user
        # and a new user is not logged in yet. It is only uploaded after the form
        # is valid, so failed signups do not leave orphan files in S3.
        profile_picture = None
        image = request.files.get('image')
        if image and image.filename:
            upload = process_and_upload_image(image)
            if 'url' not in upload:
                return {'errors': [f"image : {upload['errors']}"]}, upload.get('status', 400)
            profile_picture = upload['url']

        user = User(
            username=form.data['username'],
            email=form.data['email'],
            password=form.data['password'],
            first_name=form.data['first_name'],
            last_name=form.data['last_name'],
        )
        if profile_picture:
            user.profile_picture = profile_picture
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return user.to_dict()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@auth_routes.route('/unauthorized')
def unauthorized():
    """
    Returns unauthorized JSON when flask-login authentication fails
    """
    return {'errors': ['Unauthorized']}, 401
