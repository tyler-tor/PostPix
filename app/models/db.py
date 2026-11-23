"""The shared SQLAlchemy object and small model helpers."""
from datetime import timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, func

# Give every index and constraint a predictable name, so later migrations can
# find and change them by name (Postgres and SQLite would otherwise invent
# different names, or none).
NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}

db = SQLAlchemy(metadata=MetaData(naming_convention=NAMING_CONVENTION))


class TimestampMixin:
    """Adds created_at / updated_at, filled by the database clock
    (timezone-aware, DEFAULT now() in the table) instead of Python's local time.
    updated_at is refreshed by SQLAlchemy on every UPDATE.
    """
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=func.now(), onupdate=func.now())


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
