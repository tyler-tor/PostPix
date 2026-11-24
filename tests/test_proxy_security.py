"""P38: trusted proxy headers, same-origin CSRF behind the proxy, security headers, health."""
import pytest
from flask import request

from app import create_app
from app.models import db, User

SITE = 'postpix.tylertorrero.dev'
PROXY_HEADERS = {
    'X-Forwarded-Proto': 'https',
    'X-Forwarded-Host': SITE,
    'X-Forwarded-For': '203.0.113.9',
}


def _app_with_hops(monkeypatch, hops):
    monkeypatch.setenv('TRUSTED_PROXY_HOPS', str(hops))
    app = create_app('testing')

    @app.route('/api/_whoami')
    def whoami():
        return {'scheme': request.scheme, 'host': request.host, 'ip': request.remote_addr}

    return app


def test_forwarded_headers_are_trusted_when_configured(monkeypatch):
    app = _app_with_hops(monkeypatch, 1)
    body = app.test_client().get('/api/_whoami', headers=PROXY_HEADERS).get_json()
    assert body == {'scheme': 'https', 'host': SITE, 'ip': '203.0.113.9'}


def test_forwarded_headers_are_ignored_by_default(monkeypatch):
    monkeypatch.delenv('TRUSTED_PROXY_HOPS', raising=False)
    monkeypatch.delenv('TRUSTED_PROXY_HOPS_FOR', raising=False)
    app = create_app('testing')
    assert app.config['TRUSTED_PROXY_HOPS'] == 0

    @app.route('/api/_whoami')
    def whoami():
        return {'scheme': request.scheme, 'host': request.host}

    body = app.test_client().get('/api/_whoami', headers=PROXY_HEADERS).get_json()
    assert body == {'scheme': 'http', 'host': 'localhost'}


def test_production_trusts_one_hop_by_default(prod_env):
    prod_env.delenv('TRUSTED_PROXY_HOPS', raising=False)
    app = create_app('production')
    assert app.config['TRUSTED_PROXY_HOPS'] == 1
    assert app.config['TRUSTED_PROXY_HOPS_FOR'] == 1


@pytest.fixture
def csrf_app(monkeypatch):
    """Testing app with CSRF ON and the proxy trusted, like production."""
    app = _app_with_hops(monkeypatch, 1)
    app.config['WTF_CSRF_ENABLED'] = True
    with app.app_context():
        db.create_all()
        db.session.add(User(username='demo', email='demo@aa.io', password='password',
                            first_name='d', last_name='u'))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


def _login(client, referer):
    client.get('/api/auth/', headers=PROXY_HEADERS)  # sets the csrf_token cookie
    token = client.get_cookie('csrf_token').value
    return client.post('/api/auth/login',
                       json={'email': 'demo@aa.io', 'password': 'password'},
                       headers={**PROXY_HEADERS, 'X-CSRFToken': token, 'Referer': referer})


def test_same_origin_csrf_works_behind_the_proxy(csrf_app):
    response = _login(csrf_app.test_client(), f'https://{SITE}/')
    assert response.status_code == 200, response.get_json()


def test_csrf_rejects_a_foreign_referer_over_https(csrf_app):
    response = _login(csrf_app.test_client(), 'https://evil.example/')
    assert response.status_code == 400
    assert 'referrer does not match' in response.get_json()['errors'][0]


def test_csrf_rejects_a_missing_token(csrf_app):
    client = csrf_app.test_client()
    response = client.post('/api/auth/login', json={'email': 'demo@aa.io', 'password': 'password'},
                           headers={**PROXY_HEADERS, 'Referer': f'https://{SITE}/'})
    assert response.status_code == 400


def test_security_headers_on_api_responses(client):
    headers = client.get('/api/health').headers
    assert headers['X-Content-Type-Options'] == 'nosniff'
    assert headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'
    assert headers['X-Frame-Options'] == 'DENY'
    assert headers['Content-Security-Policy'] == "default-src 'none'; frame-ancestors 'none'"
    assert headers['Cross-Origin-Resource-Policy'] == 'same-origin'
    assert headers['Cache-Control'] == 'no-store'
    assert 'Strict-Transport-Security' not in headers  # not in development/testing


def test_hsts_in_production(prod_env):
    headers = create_app('production').test_client().get('/api/health').headers
    assert headers['Strict-Transport-Security'] == 'max-age=31536000'
    prod_env.setenv('HSTS_SECONDS', '0')
    headers = create_app('production').test_client().get('/api/health').headers
    assert 'Strict-Transport-Security' not in headers


def test_health_sets_no_cookies(client):
    response = client.get('/api/health')
    assert response.get_json() == {'status': 'ok'}
    assert 'Set-Cookie' not in response.headers
    # Other API responses still hand out the CSRF cookie.
    assert 'csrf_token' in client.get('/api/auth/').headers.get('Set-Cookie', '')


def test_health_db_ok(client):
    response = client.get('/api/health/db')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok', 'database': 'ok'}


def test_health_db_reports_503_when_the_database_is_unreachable(monkeypatch, tmp_path):
    monkeypatch.setenv('TEST_DATABASE_URL', f'sqlite:///{tmp_path}/missing-dir/x.db')
    app = create_app('testing')
    response = app.test_client().get('/api/health/db')
    assert response.status_code == 503
    assert response.get_json() == {'status': 'error', 'database': 'unreachable'}
    # The liveness check does not care.
    assert app.test_client().get('/api/health').status_code == 200
