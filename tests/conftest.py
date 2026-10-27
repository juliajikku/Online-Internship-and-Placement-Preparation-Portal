import bcrypt
import pytest

from app import create_app
from app.db import get_db, utcnow

PASSWORD = "Str0ng-test-pass"


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"), "SECRET_KEY": "test-key"})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(app, email, role, status="active", name="Test User", company=None, password=PASSWORD):
    with app.app_context():
        db = get_db()
        cur = db.execute(
            "INSERT INTO users (name, email, password_hash, role, status, company_name, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, bcrypt.hashpw(password.encode(), bcrypt.gensalt()), role, status, company, utcnow().isoformat()),
        )
        db.commit()
        return cur.lastrowid


def _csrf(client):
    """Load a page so the session has a CSRF token, then return it."""
    client.get("/login")
    with client.session_transaction() as sess:
        return sess["csrf"]


def post(client, url, data=None):
    data = dict(data or {})
    data["csrf_token"] = _csrf(client)
    return client.post(url, data=data)


def login(client, email, password=PASSWORD):
    return post(client, "/login", {"email": email, "password": password})
