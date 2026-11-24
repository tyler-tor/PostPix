"""Configuration classes, chosen by create_app().

Which class is used:
  create_app('production' | 'development' | 'testing'), or, with no argument,
  the FLASK_ENV environment variable (default: development).

Nothing here reads required settings at import time, so importing the app
package never crashes; ProdConfig checks its settings when create_app() runs.
"""
import os
import secrets

from sqlalchemy.engine import make_url


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _normalize_db_url(url):
    """Use the psycopg 3 driver for Postgres URLs.

    SQLAlchemy only accepts 'postgresql://' (some hosts hand out 'postgres://'),
    and a plain 'postgresql://' means the old psycopg2 driver, which we no
    longer install. Both become 'postgresql+psycopg://'.
    """
    for prefix in ('postgres://', 'postgresql://'):
        if url.startswith(prefix):
            return 'postgresql+psycopg://' + url[len(prefix):]
    return url


def _env_int(name, default):
    value = os.environ.get(name)
    return int(value) if value not in (None, '') else default


def _engine_options(url):
    """SQLAlchemy engine settings for the database in `url`.

    Postgres (production: AWS RDS, shared by several apps) gets a small,
    self-healing connection pool:
      * pool_pre_ping: test a pooled connection before using it, so a
        connection RDS closed (restart, failover, idle timeout) is replaced
        instead of failing a request.
      * pool_recycle: replace connections older than DB_POOL_RECYCLE seconds.
      * pool_size / max_overflow: at most DB_POOL_SIZE + DB_MAX_OVERFLOW
        connections per gunicorn worker process (default 5 + 2; with 2
        workers that is at most 14 for this app on the shared instance).
      * DATABASE_SSLMODE: passed to psycopg as sslmode (use "require" for RDS;
        "verify-full" also needs the RDS CA bundle, see CHANGES.md P34).
    SQLite (local development, tests) needs none of this.
    """
    if not url or not url.startswith('postgresql'):
        return {}
    connect_args = {
        'connect_timeout': _env_int('DB_CONNECT_TIMEOUT', 10),
        'application_name': os.environ.get('DB_APPLICATION_NAME', 'postpix'),
    }
    sslmode = os.environ.get('DATABASE_SSLMODE')
    if sslmode:
        connect_args['sslmode'] = sslmode
    sslrootcert = os.environ.get('DATABASE_SSLROOTCERT')
    if sslrootcert:
        connect_args['sslrootcert'] = sslrootcert
    return {
        'pool_pre_ping': True,
        'pool_recycle': _env_int('DB_POOL_RECYCLE', 300),
        'pool_size': _env_int('DB_POOL_SIZE', 5),
        'max_overflow': _env_int('DB_MAX_OVERFLOW', 2),
        'connect_args': connect_args,
    }


def _with_password(url, password):
    """Put `password` into a Postgres URL, escaped correctly.

    RDS-generated passwords often contain characters such as @ / : # that
    break a hand-written URL. With DATABASE_PASSWORD set, DATABASE_URL can be
    written without a password (postgresql://postpix@host:5432/postpix).
    """
    if not url or not password or not url.startswith('postgresql'):
        return url
    return make_url(url).set(password=password).render_as_string(hide_password=False)


class Config:
    """Settings shared by every environment."""
    IS_PRODUCTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Reject request bodies (uploads) over 10 MB with 413 Payload Too Large.
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # Cookie hardening. Secure = only sent over HTTPS (production only, so
    # local http://localhost still works). Lax = not sent on cross-site
    # POSTs/iframes (extra CSRF defence) but still sent when following a link.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    def __init__(self):
        # Read the environment when the app is created, not at import time.
        # Off by default: echoing every SQL query slows the app and can leak
        # data into logs. Set SQLALCHEMY_ECHO=true locally when debugging.
        self.SQLALCHEMY_ECHO = _env_bool('SQLALCHEMY_ECHO', False)
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        url = os.environ.get('DATABASE_URL')
        self.SQLALCHEMY_DATABASE_URI = _normalize_db_url(url) if url else None
        # Serve the React build (react-app/build) from Flask? On by default for
        # local development; OFF in production, where the frontend is static
        # files on S3 + CloudFront and this app is API-only (the Docker image
        # does not contain the build). SERVE_FRONTEND=true turns it back on.
        self.SERVE_FRONTEND = _env_bool('SERVE_FRONTEND', not self.IS_PRODUCTION)

        # Images (P37). boto3 finds credentials by itself (default chain): the
        # EC2 instance role in production, AWS_PROFILE / `aws sso login`
        # locally. There are deliberately no access-key settings here.
        self.S3_BUCKET = os.environ.get('S3_BUCKET') or None
        self.AWS_REGION = (os.environ.get('AWS_REGION')
                           or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-2')
        # Public base URL of the bucket's files (CloudFront), e.g.
        # https://postpix.tylertorrero.dev/media. See app/media.py.
        self.MEDIA_BASE_URL = (os.environ.get('MEDIA_BASE_URL') or '').strip().rstrip('/')


class DevConfig(Config):
    """Local development: SQLite by default, random key if none is set."""

    def __init__(self):
        super().__init__()
        if not self.SECRET_KEY:
            # A random key per process (sessions reset on restart). Fine locally.
            self.SECRET_KEY = secrets.token_hex(32)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class TestConfig(Config):
    """Automated tests: in-memory SQLite, CSRF off, fixed key."""
    TESTING = True
    WTF_CSRF_ENABLED = False

    def __init__(self):
        super().__init__()
        self.SECRET_KEY = 'test-secret-key'
        self.SQLALCHEMY_DATABASE_URI = _normalize_db_url(
            os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:'))
        self.SQLALCHEMY_ECHO = False


class ProdConfig(Config):
    """Production: secure cookies, and refuse to start without real settings."""
    IS_PRODUCTION = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    def __init__(self):
        super().__init__()
        if not self.SECRET_KEY:
            # Fail fast: without a secret key anyone could forge session cookies.
            raise RuntimeError(
                'SECRET_KEY is not set. Generate one with: '
                'python -c "import secrets; print(secrets.token_hex(32))"')
        if not self.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError('DATABASE_URL is not set.')


CONFIGS = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig,
}


def get_config(name=None):
    """Return a config object for `name` (or FLASK_ENV, default development)."""
    name = name or os.environ.get('FLASK_ENV') or 'development'
    if name not in CONFIGS:
        raise RuntimeError(
            f'Unknown config {name!r}; use one of: {", ".join(CONFIGS)}')
    config = CONFIGS[name]()
    # Done after the class has picked its final database URL (tests and local
    # development may replace it), so the options match the real database.
    config.SQLALCHEMY_DATABASE_URI = _with_password(
        config.SQLALCHEMY_DATABASE_URI, os.environ.get('DATABASE_PASSWORD'))
    config.SQLALCHEMY_ENGINE_OPTIONS = _engine_options(config.SQLALCHEMY_DATABASE_URI)
    return config
