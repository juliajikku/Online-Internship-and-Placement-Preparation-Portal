"""NFR4 (many users at once) and NFR5 (availability) checks."""
import threading

from app.db import get_db
from tests.conftest import PASSWORD, login, make_user


def test_health_endpoint_reports_ok_without_login(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok" and resp.get_json()["database"] == "ok"


def test_health_endpoint_reports_503_when_database_is_down(client, app, monkeypatch):
    def broken():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("app.health.get_db", broken)
    resp = client.get("/health")
    assert resp.status_code == 503 and resp.get_json()["status"] == "unavailable"


def test_database_uses_wal_mode_and_busy_timeout(app):
    with app.app_context():
        db = get_db()
        assert db.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert db.execute("PRAGMA busy_timeout").fetchone()[0] >= 5000


def test_many_students_can_log_in_and_browse_at_the_same_time(app):
    """A small in-process version of the load test: 20 simultaneous users must all succeed."""
    for i in range(20):
        make_user(app, f"user{i}@pes.edu", "student", name=f"User {i}")
    results = []

    def one_user(i):
        client = app.test_client()
        ok = login(client, f"user{i}@pes.edu").status_code == 302
        ok = ok and client.get("/listings").status_code == 200 and client.get("/scores").status_code == 200
        results.append(ok)

    threads = [threading.Thread(target=one_user, args=(i,)) for i in range(20)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert results.count(True) == 20
