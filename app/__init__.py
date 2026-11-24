"""PostPix Flask application.

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
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix

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

    # Behind CloudFront + Caddy, trust their X-Forwarded-* headers so
    # request.scheme is "https", request.host is the public site name and
    # request.remote_addr is the visitor. Flask-WTF's CSRF check compares the
    # Referer with https://<request.host>/ on HTTPS requests, so the host must
    # be the public one. Off unless TRUSTED_PROXY_HOPS / _FOR are set (P38).
    hops = app.config['TRUSTED_PROXY_HOPS']
    for_hops = app.config['TRUSTED_PROXY_HOPS_FOR']
    if hops or for_hops:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=for_hops, x_proto=hops, x_host=hops)

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
        # Health checks run every few seconds from Docker/monitoring and need
        # no session, so they get no cookies (and no session work).
        if not request.path.startswith('/api/health'):
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

    @app.after_request
    def security_headers(response):
        # P38. The React site's own headers (its Content-Security-Policy etc.)
        # are set by CloudFront, which serves it from S3; these cover what
        # Flask answers, mostly JSON.
        headers = response.headers
        headers.setdefault('X-Content-Type-Options', 'nosniff')
        # Full URL to our own origin (Flask-WTF checks it on HTTPS), only the
        # origin to other sites. Never "no-referrer": that breaks CSRF checks.
        headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        headers.setdefault('X-Frame-Options', 'DENY')
        if request.path.startswith('/api/'):
            # JSON never needs to load anything or be framed.
            headers.setdefault('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'")
            headers.setdefault('Cross-Origin-Resource-Policy', 'same-origin')
        if app.config['IS_PRODUCTION'] and app.config['HSTS_SECONDS']:
            headers.setdefault('Strict-Transport-Security', f"max-age={app.config['HSTS_SECONDS']}")
        return response

    @app.route('/api/health')
    def health():
        # Liveness check for Docker / Caddy / CloudFront: the process answers.
        # No login, no database, no cookies, so it stays cheap and a database
        # hiccup never makes Docker restart a healthy container.
        return {'status': 'ok'}

    @app.route('/api/health/db')
    def health_db():
        # Optional readiness check: one trivial query. For monitoring and
        # deploy scripts, NOT for the Docker HEALTHCHECK (see above).
        try:
            db.session.execute(text('SELECT 1'))
        except Exception:
            app.logger.exception('Database health check failed')
            db.session.rollback()
            return {'status': 'error', 'database': 'unreachable'}, 503
        return {'status': 'ok', 'database': 'ok'}

    # The React build is only served when SERVE_FRONTEND is on (local
    # development). In production the API is API-only: CloudFront serves the
    # site from S3 and sends only /api/* here, so any other path is a 404.
    if app.config['SERVE_FRONTEND']:
        _register_frontend_routes(app)

    return app


def _register_frontend_routes(app):
    """Serve react-app/build: real files as-is, every other URL gets index.html."""

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
