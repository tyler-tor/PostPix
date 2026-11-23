import os

IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _secret_key():
    key = os.environ.get('SECRET_KEY')
    if not key:
        if IS_PRODUCTION:
            # Fail fast: without a secret key anyone could forge session cookies.
            raise RuntimeError(
                'SECRET_KEY is not set. Generate one with: '
                'python -c "import secrets; print(secrets.token_hex(32))"')
        # Local development only: a random key per process (sessions reset on restart).
        import secrets
        key = secrets.token_hex(32)
    return key


def _database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        if IS_PRODUCTION:
            raise RuntimeError('DATABASE_URL is not set.')
        url = 'sqlite:///dev.db'
    # SQLAlchemy 1.4 no longer supports url strings that start with 'postgres'
    # (only 'postgresql') but some hosts (Heroku) still hand out 'postgres://'.
    return url.replace('postgres://', 'postgresql://', 1)


class Config:
    SECRET_KEY = _secret_key()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _database_url()
    # Off by default: echoing every SQL query slows the app and can leak data
    # into logs. Set SQLALCHEMY_ECHO=true locally when debugging queries.
    SQLALCHEMY_ECHO = _env_bool('SQLALCHEMY_ECHO', False)
    # Reject request bodies (uploads) over 10 MB with 413 Payload Too Large.
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # Cookie hardening. Secure = only sent over HTTPS (production only, so
    # local http://localhost still works). Lax = not sent on cross-site
    # POSTs/iframes (extra CSRF defence) but still sent when following a link.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = IS_PRODUCTION
    REMEMBER_COOKIE_SAMESITE = 'Lax'
