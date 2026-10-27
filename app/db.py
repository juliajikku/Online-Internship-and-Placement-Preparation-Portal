"""SQLite helpers: connection handling, schema, and a small audit-log helper."""
import sqlite3
from datetime import datetime, timezone

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    password_hash   BLOB    NOT NULL,
    role            TEXT    NOT NULL CHECK (role IN ('student', 'recruiter', 'admin')),
    status          TEXT    NOT NULL CHECK (status IN ('active', 'pending', 'rejected')),
    company_name    TEXT,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT,
    created_at      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    action     TEXT NOT NULL,
    detail     TEXT,
    created_at TEXT NOT NULL
);
"""


def utcnow():
    return datetime.now(timezone.utc)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    get_db().executescript(SCHEMA)
    get_db().commit()


def init_app(app):
    app.teardown_appcontext(close_db)


def log_action(user_id, action, detail=""):
    """SE-06: record key actions (logins, failures, approvals) with a timestamp."""
    get_db().execute(
        "INSERT INTO audit_log (user_id, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (user_id, action, detail, utcnow().isoformat()),
    )
    get_db().commit()
