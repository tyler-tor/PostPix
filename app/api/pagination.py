"""Cursor pagination helpers shared by the list endpoints.

Why cursors and not page numbers: with "page 2" a new post arriving while you
scroll shifts every item and you see a duplicate. A cursor says "continue after
THIS item", so the list stays stable. The cursor is opaque to the frontend: it
reads `nextCursor` from a response and sends it back unchanged.

  Posts (newest first)      ?limit=12&before=<created_at>,<id>
  Comments (oldest first)   ?limit=20&after=<created_at>,<id>
  People / likers lists     ?limit=30&after=<id>

Every paginated response carries "nextCursor": the value to send for the next
page, or null when there is nothing more.
"""
from datetime import datetime, timezone

from flask import request
from sqlalchemy import String, and_, or_, type_coerce, literal
from app.models import db


def get_limit(default, maximum):
    """?limit=N, clamped to 1..maximum (bad values fall back to the default)."""
    try:
        value = int(request.args.get('limit', default))
    except ValueError:
        value = default
    return max(1, min(value, maximum))


def encode_time_cursor(created_at, row_id):
    if created_at.tzinfo is None:  # SQLite returns naive UTC datetimes
        created_at = created_at.replace(tzinfo=timezone.utc)
    # "Z" instead of "+00:00": a plus sign in a query string turns into a space.
    stamp = created_at.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    return f'{stamp},{row_id}'


def decode_time_cursor(raw):
    """"<iso datetime>,<id>" -> (aware datetime, int), or None if absent.
    A malformed cursor raises ValueError (the route turns it into a 400)."""
    if not raw:
        return None
    stamp, _, row_id = raw.rpartition(',')
    when = datetime.fromisoformat(stamp)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc), int(row_id)


def _time_param(when):
    """The comparison value for a created_at column.

    SQLite keeps timestamps as text ("2026-11-23 18:04:05", written by
    CURRENT_TIMESTAMP, no fraction) and compares them as text, so the cursor
    must be written in the same format. Postgres compares real timestamps.
    """
    if db.engine.dialect.name == 'sqlite':
        fmt = '%Y-%m-%d %H:%M:%S.%f' if when.microsecond else '%Y-%m-%d %H:%M:%S'
        return when.strftime(fmt)
    return when


def _column(created_col):
    return type_coerce(created_col, String) if db.engine.dialect.name == 'sqlite' else created_col


def _param(when):
    value = _time_param(when)
    return literal(value, type_=String) if isinstance(value, str) else value


def older_than(created_col, id_col, cursor):
    """Rows strictly older than the cursor in (created_at DESC, id DESC) order."""
    when, row_id = cursor
    col, param = _column(created_col), _param(when)
    return or_(col < param, and_(col == param, id_col < row_id))


def newer_than(created_col, id_col, cursor):
    """Rows strictly newer than the cursor in (created_at ASC, id ASC) order."""
    when, row_id = cursor
    col, param = _column(created_col), _param(when)
    return or_(col > param, and_(col == param, id_col > row_id))


def bad_cursor():
    return {'errors': ['Invalid cursor']}, 400
