"""JSON error responses for the API.

Every error the API returns has the same shape: ``{"errors": ["message", ...]}``
with the right HTTP status code, so the frontend can always do
``if (!response.ok) { const { errors } = await response.json() }``.
"""
from flask import request
from werkzeug.exceptions import HTTPException


def _is_api_request():
    return request.path.startswith('/api/')


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        # Non-API paths (the React app) keep Flask's normal behaviour.
        if not _is_api_request():
            return e
        return {'errors': [e.description or e.name]}, e.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        if isinstance(e, HTTPException):
            return handle_http_exception(e)
        # Log the full traceback on the server, but never send it to the client.
        app.logger.exception('Unhandled error on %s %s', request.method, request.path)
        if app.config.get('TESTING') or app.debug:
            raise e
        return {'errors': ['Internal server error']}, 500
