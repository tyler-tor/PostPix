from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError, generate_csrf
from flask_login import LoginManager

from .models import db, User
from .api.user_routes import user_routes
from .api.auth_routes import auth_routes
from .api.post_routes import post_routes
from .api.me_routes import me_routes
from .api.comment_routes import comment_routes
from .api.img_routes import img_routes

from .seeds import seed_commands

from .config import Config, IS_PRODUCTION
from .errors import register_error_handlers


app = Flask(__name__, static_folder='../react-app/build', static_url_path='/')

# Setup login manager
login = LoginManager(app)
login.login_view = 'auth.unauthorized'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@login.unauthorized_handler
def unauthorized():
    # Logged-out API calls get a JSON 401 instead of a redirect.
    return {'errors': ['Unauthorized']}, 401


# Tell flask about our seed commands
app.cli.add_command(seed_commands)

app.config.from_object(Config)
app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(post_routes, url_prefix='/api/posts')
app.register_blueprint(me_routes, url_prefix='/api/me')
app.register_blueprint(comment_routes, url_prefix='/api/comments')
app.register_blueprint(img_routes, url_prefix='/api/img')
db.init_app(app)
Migrate(app, db)

# Application Security
# (flask-cors was removed: the React build is served from the same origin as
# the API, so cross-origin requests are not needed and should not be allowed.)
# Check a CSRF token on every POST/PUT/PATCH/DELETE (not just routes that use a
# WTForm). The frontend sends the token in the X-CSRFToken header (apiFetch.js).
csrf = CSRFProtect(app)


register_error_handlers(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return {'errors': [f'CSRF check failed: {e.description}']}, 400




@app.after_request
def inject_csrf_token(response):
    response.set_cookie(
        'csrf_token',
        generate_csrf(),
        secure=IS_PRODUCTION,
        samesite='Lax',
        # Must be readable by JavaScript so apiFetch can copy it into the
        # X-CSRFToken header. The token alone is not a secret: an attacker's
        # site cannot read our cookies, which is what makes this safe.
        httponly=False)
    return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def react_root(path):
    # Unknown /api/... URLs are real 404s, not the React page.
    if path.startswith('api/'):
        return {'errors': ['Not found']}, 404
    if path == 'favicon.ico':
        return app.send_static_file('favicon.ico')
    return app.send_static_file('index.html')
