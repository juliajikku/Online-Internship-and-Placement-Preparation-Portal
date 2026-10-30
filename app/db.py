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

CREATE TABLE IF NOT EXISTS student_profiles (
    user_id     INTEGER PRIMARY KEY REFERENCES users(id),
    cgpa        REAL    NOT NULL,
    branch      TEXT    NOT NULL,
    skills      TEXT,
    resume_file TEXT,
    resume_name TEXT,
    updated_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS recruiter_profiles (
    user_id     INTEGER PRIMARY KEY REFERENCES users(id),
    description TEXT,
    website     TEXT,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS listings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiter_id INTEGER NOT NULL REFERENCES users(id),
    role        TEXT    NOT NULL,
    domain      TEXT    NOT NULL,
    location    TEXT    NOT NULL,
    min_cgpa    REAL    NOT NULL,
    branches    TEXT,
    stipend     INTEGER NOT NULL,
    deadline    TEXT    NOT NULL,
    description TEXT,
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id  INTEGER NOT NULL REFERENCES listings(id),
    student_id  INTEGER NOT NULL REFERENCES users(id),
    status      TEXT    NOT NULL,
    applied_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL,
    UNIQUE (listing_id, student_id)
);

CREATE TABLE IF NOT EXISTS tests (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT    NOT NULL,
    duration_minutes INTEGER NOT NULL,
    created_by       INTEGER NOT NULL REFERENCES users(id),
    created_at       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id  INTEGER NOT NULL REFERENCES tests(id),
    text     TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct  TEXT NOT NULL CHECK (correct IN ('a', 'b', 'c', 'd'))
);

CREATE TABLE IF NOT EXISTS attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id      INTEGER NOT NULL REFERENCES tests(id),
    student_id   INTEGER NOT NULL REFERENCES users(id),
    started_at   TEXT    NOT NULL,
    submitted_at TEXT,
    score        INTEGER,
    total        INTEGER,
    question_order TEXT NOT NULL,
    answers      TEXT NOT NULL DEFAULT '{}'
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
