"""P33: production is API-only; local development still serves the React build."""
from app import create_app


def test_production_does_not_serve_the_frontend(prod_env):
    app = create_app('production')
    client = app.test_client()
    assert app.config['SERVE_FRONTEND'] is False
    assert client.get('/api/health').get_json() == {'status': 'ok'}
    # No catch-all route: the site comes from S3/CloudFront, not from Flask.
    assert client.get('/').status_code == 404
    assert client.get('/explore').status_code == 404
    assert 'react_root' not in app.view_functions


def test_production_can_opt_back_in(prod_env):
    prod_env.setenv('SERVE_FRONTEND', 'true')
    assert create_app('production').config['SERVE_FRONTEND'] is True


def test_development_serves_the_frontend(tmp_path, monkeypatch):
    monkeypatch.delenv('SERVE_FRONTEND', raising=False)
    (tmp_path / 'index.html').write_text('<!doctype html><title>PostPix</title>')
    app = create_app('development')
    app.config['FRONTEND_DIST'] = str(tmp_path)
    response = app.test_client().get('/explore')
    assert response.status_code == 200
    assert b'PostPix' in response.data
    # Unknown API URLs are still JSON 404s, never the React page.
    assert app.test_client().get('/api/nope').status_code == 404
