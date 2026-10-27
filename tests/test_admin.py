from app.db import get_db
from tests.conftest import login, make_user, post


def status_of(app, user_id):
    with app.app_context():
        return get_db().execute("SELECT status FROM users WHERE id = ?", (user_id,)).fetchone()["status"]


def test_admin_sees_pending_recruiters(client, app):
    make_user(app, "admin@portal.local", "admin")
    make_user(app, "r@acme.com", "recruiter", status="pending", name="Ravi", company="Acme Corp")
    login(client, "admin@portal.local")
    resp = client.get("/admin/")
    assert resp.status_code == 200
    assert b"Acme Corp" in resp.data and b"Approve" in resp.data


def test_admin_can_approve_recruiter(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "admin@portal.local")
    resp = post(client, f"/admin/recruiters/{rid}/approve")
    assert resp.status_code == 302
    assert status_of(app, rid) == "active"


def test_admin_can_reject_recruiter(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "admin@portal.local")
    post(client, f"/admin/recruiters/{rid}/reject")
    assert status_of(app, rid) == "rejected"


def test_approval_is_written_to_audit_log(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "admin@portal.local")
    post(client, f"/admin/recruiters/{rid}/approve")
    with app.app_context():
        actions = [r["action"] for r in get_db().execute("SELECT action FROM audit_log")]
    assert "RECRUITER_APPROVED" in actions


def test_already_reviewed_recruiter_cannot_be_changed(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", status="rejected", company="Acme")
    login(client, "admin@portal.local")
    post(client, f"/admin/recruiters/{rid}/approve")
    assert status_of(app, rid) == "rejected"


def test_student_cannot_open_admin_page_or_approve(client, app):
    make_user(app, "s@pes.edu", "student")
    rid = make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "s@pes.edu")
    assert client.get("/admin/").status_code == 403
    assert post(client, f"/admin/recruiters/{rid}/approve").status_code == 403
    assert status_of(app, rid) == "pending"


def test_recruiter_cannot_approve_themselves(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "r@acme.com")
    assert post(client, f"/admin/recruiters/{rid}/approve").status_code == 403
    assert status_of(app, rid) == "pending"


def test_pending_recruiter_sees_awaiting_approval_message(client, app):
    make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "r@acme.com")
    assert b"Awaiting Admin approval" in client.get("/recruiter").data


def test_approved_recruiter_sees_approved_badge(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "admin@portal.local")
    post(client, f"/admin/recruiters/{rid}/approve")
    client.get("/logout")
    post(client, "/logout")
    login(client, "r@acme.com")
    assert b"Approved" in client.get("/recruiter").data


def test_unknown_recruiter_id_returns_404(client, app):
    make_user(app, "admin@portal.local", "admin")
    login(client, "admin@portal.local")
    assert post(client, "/admin/recruiters/9999/approve").status_code == 404
