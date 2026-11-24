"""Shared pytest fixtures.

Every test gets a fresh app built by the factory with the testing config
(in-memory SQLite, CSRF off) and empty tables.
"""
import pytest

from app import create_app
from app.models import db


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def prod_env(monkeypatch):
    """The two variables ProdConfig refuses to start without (dummy values)."""
    monkeypatch.setenv('SECRET_KEY', 'test-only-secret')
    monkeypatch.setenv('DATABASE_URL', 'sqlite://')
    return monkeypatch
