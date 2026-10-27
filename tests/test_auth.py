from datetime import timedelta

from app.db import get_db, utcnow
from tests.conftest import PASSWORD, login, make_user, post


def user_row(app, email):
    with app.app_context():
        return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


# ---- Registration (FR1) ----
def test_student_can_register_and_is_active(client, app):
    resp = post(client, "/register", {"name": "Asha Rao", "email": "asha@pes.edu", "password": PASSWORD, "role": "student"})
    assert resp.status_code == 302
    row = user_row(app, "asha@pes.edu")
    assert row["role"] == "student" and row["status"] == "active"


def test_recruiter_registers_as_pending(client, app):
    post(client, "/register", {"name": "Ravi", "email": "ravi@acme.com", "password": PASSWORD, "role": "recruiter", "company_name": "Acme"})
    row = user_row(app, "ravi@acme.com")
    assert row["role"] == "recruiter" and row["status"] == "pending"


def test_recruiter_requires_company_name(client, app):
    resp = post(client, "/register", {"name": "Ravi", "email": "ravi@acme.com", "password": PASSWORD, "role": "recruiter"})
    assert resp.status_code == 400
    assert user_row(app, "ravi@acme.com") is None


def test_cannot_self_register_as_admin(client, app):
    resp = post(client, "/register", {"name": "Eve", "email": "eve@x.com", "password": PASSWORD, "role": "admin"})
    assert resp.status_code == 400
    assert user_row(app, "eve@x.com") is None


def test_weak_password_and_bad_email_rejected(client, app):
    resp = post(client, "/register", {"name": "Asha", "email": "not-an-email", "password": "short", "role": "student"})
    assert resp.status_code == 400


def test_duplicate_email_rejected(client, app):
    make_user(app, "dup@pes.edu", "student")
    resp = post(client, "/register", {"name": "Dup", "email": "dup@pes.edu", "password": PASSWORD, "role": "student"})
    assert resp.status_code == 400


def test_password_is_stored_hashed(client, app):
    post(client, "/register", {"name": "Asha Rao", "email": "asha@pes.edu", "password": PASSWORD, "role": "student"})
    stored = user_row(app, "asha@pes.edu")["password_hash"]
    assert PASSWORD.encode() not in stored and stored.startswith(b"$2")  # bcrypt


# ---- Login (SE-01) ----
def test_student_login_redirects_to_student_dashboard(client, app):
    make_user(app, "s@pes.edu", "student")
    resp = login(client, "s@pes.edu")
    assert resp.status_code == 302
    assert client.get("/dashboard").headers["Location"].endswith("/student")


def test_each_role_lands_on_its_own_dashboard(client, app):
    make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "r@acme.com")
    assert client.get("/dashboard").headers["Location"].endswith("/recruiter")


def test_wrong_password_gives_generic_error(client, app):
    make_user(app, "s@pes.edu", "student")
    resp = login(client, "s@pes.edu", "wrong-password")
    assert resp.status_code == 401
    assert b"Invalid email or password." in resp.data


def test_unknown_email_gives_same_generic_error(client):
    resp = login(client, "nobody@pes.edu")
    assert resp.status_code == 401
    assert b"Invalid email or password." in resp.data


def test_rejected_recruiter_cannot_log_in(client, app):
    make_user(app, "r@acme.com", "recruiter", status="rejected", company="Acme")
    resp = login(client, "r@acme.com")
    assert resp.status_code == 403


# ---- Lockout (SE-12) ----
def test_account_locks_after_five_failed_attempts(client, app):
    make_user(app, "s@pes.edu", "student")
    for _ in range(5):
        login(client, "s@pes.edu", "wrong-password")
    # Even the correct password is refused while locked.
    resp = login(client, "s@pes.edu")
    assert resp.status_code == 429


def test_lock_expires_after_lockout_period(client, app):
    make_user(app, "s@pes.edu", "student")
    for _ in range(5):
        login(client, "s@pes.edu", "wrong-password")
    with app.app_context():
        past = (utcnow() - timedelta(minutes=1)).isoformat()
        get_db().execute("UPDATE users SET locked_until = ?", (past,))
        get_db().commit()
    assert login(client, "s@pes.edu").status_code == 302


# ---- Session (SE-05) ----
def test_logout_ends_session(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    post(client, "/logout")
    assert client.get("/student").status_code == 302  # redirected to login


def test_login_is_required_for_dashboards(client):
    for url in ("/student", "/recruiter", "/admin/"):
        assert client.get(url).status_code == 302


def test_form_post_without_csrf_token_is_rejected(client):
    resp = client.post("/login", data={"email": "a@b.com", "password": "x"})
    assert resp.status_code == 400


def test_failed_login_is_written_to_audit_log(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu", "wrong-password")
    with app.app_context():
        actions = [r["action"] for r in get_db().execute("SELECT action FROM audit_log")]
    assert "LOGIN_FAILED" in actions
