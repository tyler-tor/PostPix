"""Configuration classes, chosen by create_app().

Which class is used:
  create_app('production' | 'development' | 'testing'), or, with no argument,
  the FLASK_ENV environment variable (default: development).

Nothing here reads required settings at import time, so importing the app
package never crashes; ProdConfig checks its settings when create_app() runs.
"""
import os
import secrets


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _normalize_db_url(url):
    # SQLAlchemy only accepts 'postgresql://', but some hosts hand out 'postgres://'.
    return url.replace('postgres://', 'postgresql://', 1)


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
    return CONFIGS[name]()
