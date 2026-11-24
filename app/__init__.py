"""Postpix Flask application.

Use the app factory: `create_app()` builds a new, fully configured app.
  * `flask ...` commands find it automatically (FLASK_APP=app).
  * gunicorn uses `wsgi:app` (see wsgi.py).
  * tests call `create_app('testing')` to get a fresh copy with test settings.
"""
import os

from flask import Flask, request, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError, generate_csrf

from .config import get_config
from .errors import register_error_handlers
from .models import db, User

# Extensions are created once here and attached to each app in create_app().
login = LoginManager()
migrate = Migrate()
# Check a CSRF token on every POST/PUT/PATCH/DELETE (not just routes that use a
# WTForm). The frontend sends the token in the X-CSRFToken header (apiFetch.js).
csrf = CSRFProtect()


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


@login.unauthorized_handler
def unauthorized():
    # Logged-out API calls get a JSON 401 instead of a redirect.
    return {'errors': ['Unauthorized']}, 401


def create_app(config_name=None):
    """Build the app. config_name: 'development', 'testing' or 'production'
    (default: the FLASK_ENV environment variable, else 'development')."""
    # static_folder=None: the React build is served by react_root() below, so
    # Flask's own /<path> static route can't answer deep links like /explore
    # with a 404 before the React app gets a chance to handle them.
    app = Flask(__name__, static_folder=None)
    app.config.setdefault('FRONTEND_DIST', os.path.abspath(
        os.path.join(app.root_path, '..', 'react-app', 'build')))
    app.config.from_object(get_config(config_name))

    # Extensions
    db.init_app(app)
    # render_as_batch: lets future migrations ALTER tables on SQLite too
    # (SQLite can't alter constraints in place; Alembic rebuilds the table).
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)
    login.login_view = 'auth.unauthorized'
    # (flask-cors was removed: the React build is served from the same origin as
    # the API, so cross-origin requests are not needed and should not be allowed.)
    csrf.init_app(app)

    # Blueprints (imported here so importing the package stays cheap and free
    # of circular imports).
    from .api.user_routes import user_routes
    from .api.auth_routes import auth_routes
    from .api.post_routes import post_routes
    from .api.me_routes import me_routes
    from .api.comment_routes import comment_routes
    from .api.img_routes import img_routes
    app.register_blueprint(user_routes, url_prefix='/api/users')
    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(post_routes, url_prefix='/api/posts')
    app.register_blueprint(me_routes, url_prefix='/api/me')
    app.register_blueprint(comment_routes, url_prefix='/api/comments')
    app.register_blueprint(img_routes, url_prefix='/api/img')

    # `flask seed ...` commands
    from .seeds import seed_commands
    app.cli.add_command(seed_commands)

    register_error_handlers(app)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return {'errors': [f'CSRF check failed: {e.description}']}, 400

    @app.after_request
    def inject_csrf_token(response):
        response.set_cookie(
            'csrf_token',
            generate_csrf(),
            secure=app.config['IS_PRODUCTION'],
            samesite='Lax',
            # Must be readable by JavaScript so apiFetch can copy it into the
            # X-CSRFToken header. The token alone is not a secret: an attacker's
            # site cannot read our cookies, which is what makes this safe.
            httponly=False)
        # Never let a browser or CDN keep an API answer (it is per-user data).
        if request.path.startswith('/api/'):
            response.headers.setdefault('Cache-Control', 'no-store')
        return response

    @app.route('/api/health')
    def health():
        # Used by Docker / load balancer health checks. No login, no DB.
        return {'status': 'ok'}

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def react_root(path):
        # Unknown /api/... URLs are real 404s, not the React page.
        if path.startswith('api/'):
            return {'errors': ['Not found']}, 404
        dist = app.config['FRONTEND_DIST']
        # Real files from the build (assets/*.js, favicon.ico, ...) are sent as-is.
        # send_from_directory refuses paths that try to leave the folder.
        if path and os.path.isfile(os.path.join(dist, path)):
            # assets/ files have a content hash in their name (index-3f9a2c.js),
            # so a changed file always gets a new URL and can be cached for a
            # year. Other files (favicon...) are cached for an hour.
            max_age = 31536000 if path.startswith('assets/') else 3600
            response = send_from_directory(dist, path, max_age=max_age)
            if path.startswith('assets/'):
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            return response
        # A missing *file* (e.g. an old /assets/index-abc123.js) is a real 404;
        # serving index.html there would confuse the browser.
        if '.' in path.rsplit('/', 1)[-1]:
            return {'errors': ['Not found']}, 404
        # Every other URL (/, /explore, /42, /no-such-page) gets index.html and
        # React Router decides what to show, including its own 404 page.
        # no-cache = always check with the server (cheap, answered with 304),
        # so a new deploy is picked up at once and points at the new hashed files.
        response = send_from_directory(dist, 'index.html', max_age=0)
        response.headers['Cache-Control'] = 'no-cache'
        return response

    return app
