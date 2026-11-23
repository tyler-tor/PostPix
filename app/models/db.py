# models/db.py file

from datetime import timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# add import and set variable to access flask environment
import os
environment = os.getenv("FLASK_ENV")
SCHEMA = os.environ.get('SCHEMA')


db = SQLAlchemy()

# add function to add a prefix to table names in production environment only
def add_prefix_for_prod(attr):
    if environment == "production":
        return f"{SCHEMA}.{attr}"
    else:
        return attr


class TimestampMixin:
    """Adds created_at / updated_at, filled by the database clock
    (timezone-aware) instead of Python's local time.

    server_default puts DEFAULT now() in the table definition (new migrations);
    default=func.now() makes SQLAlchemy send now() itself, so inserts also work
    on tables created by the old migrations, which have no server default.
    """
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=func.now(), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=func.now(), server_default=func.now(),
                           onupdate=func.now())


def iso(value):
    """Datetime -> ISO-8601 string for JSON (e.g. 2026-11-23T18:04:05+00:00).

    SQLite gives back naive datetimes; the database clock (CURRENT_TIMESTAMP)
    is UTC, so naive values are marked as UTC.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
