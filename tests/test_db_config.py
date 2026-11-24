"""P34: database settings for RDS Postgres (no real database needed)."""
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.config import get_config


def test_postgres_gets_pool_and_ssl_options(prod_env):
    prod_env.setenv('DATABASE_URL', 'postgres://postpix:pw@db.example.com:5432/postpix')
    prod_env.setenv('DATABASE_SSLMODE', 'require')
    config = get_config('production')
    assert config.SQLALCHEMY_DATABASE_URI.startswith('postgresql+psycopg://')
    options = config.SQLALCHEMY_ENGINE_OPTIONS
    assert options['pool_pre_ping'] is True
    assert options['connect_args']['sslmode'] == 'require'
    assert options['pool_size'] == 5 and options['max_overflow'] == 2
    # SQLAlchemy + psycopg 3 accept these options (create_engine does not connect).
    create_engine(config.SQLALCHEMY_DATABASE_URI, **options).dispose()


def test_password_with_special_characters_is_escaped(prod_env):
    prod_env.setenv('DATABASE_URL', 'postgresql://postpix@db.example.com:5432/postpix')
    prod_env.setenv('DATABASE_PASSWORD', 'p@ss:w/rd#1')
    url = make_url(get_config('production').SQLALCHEMY_DATABASE_URI)
    assert url.password == 'p@ss:w/rd#1'
    assert url.host == 'db.example.com' and url.database == 'postpix'


def test_sqlite_gets_no_pool_options(prod_env):
    prod_env.setenv('DATABASE_URL', 'sqlite:///dev.db')
    prod_env.setenv('DATABASE_SSLMODE', 'require')
    assert get_config('production').SQLALCHEMY_ENGINE_OPTIONS == {}
    assert get_config('testing').SQLALCHEMY_ENGINE_OPTIONS == {}
