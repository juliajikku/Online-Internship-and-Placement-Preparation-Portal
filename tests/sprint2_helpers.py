import io
import json
from datetime import timedelta

from app.db import get_db, utcnow
from tests.conftest import PASSWORD, login, make_user, post  # noqa: F401

PDF = b"%PDF-1.4 fake but valid header"
FUTURE = (utcnow() + timedelta(days=30)).date().isoformat()
PAST = (utcnow() - timedelta(days=2)).date().isoformat()


# ------------------------------------------------------------------ helpers
def logout(client):
    post(client, "/logout")


def set_profile(app, user_id, cgpa=8.0, branch="CSE", resume=True):
    with app.app_context():
        get_db().execute(
            "INSERT OR REPLACE INTO student_profiles (user_id, cgpa, branch, skills, resume_file, resume_name, updated_at)"
            " VALUES (?, ?, ?, '', ?, ?, ?)",
            (user_id, cgpa, branch, "r.pdf" if resume else None, "r.pdf" if resume else None, utcnow().isoformat()),
        )
        get_db().commit()


def add_listing(app, recruiter_id, role="SDE Intern", min_cgpa=7.0, branches="", stipend=20000, deadline=FUTURE, domain="Software", location="Bengaluru"):
    with app.app_context():
        cur = get_db().execute(
            "INSERT INTO listings (recruiter_id, role, domain, location, min_cgpa, branches, stipend, deadline, description, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', ?)",
            (recruiter_id, role, domain, location, min_cgpa, branches, stipend, deadline, utcnow().isoformat()),
        )
        get_db().commit()
        return cur.lastrowid


def add_application(app, listing_id, student_id, status="Applied"):
    with app.app_context():
        now = utcnow().isoformat()
        cur = get_db().execute(
            "INSERT INTO applications (listing_id, student_id, status, applied_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (listing_id, student_id, status, now, now),
        )
        get_db().commit()
        return cur.lastrowid


def app_status(app, application_id):
    with app.app_context():
        return get_db().execute("SELECT status FROM applications WHERE id = ?", (application_id,)).fetchone()["status"]


def upload(client, url, data, file_tuple):
    client.get("/login")
    with client.session_transaction() as sess:
        token = sess["csrf"]
    payload = dict(data, csrf_token=token, resume=file_tuple)
    return client.post(url, data=payload, content_type="multipart/form-data")


def make_test(app, admin_id, n_questions=4, minutes=10):
    with app.app_context():
        db = get_db()
        tid = db.execute(
            "INSERT INTO tests (title, duration_minutes, created_by, created_at) VALUES ('Quant 1', ?, ?, ?)",
            (minutes, admin_id, utcnow().isoformat()),
        ).lastrowid
        qids = []
        for i in range(n_questions):
            qids.append(
                db.execute(
                    "INSERT INTO questions (test_id, text, option_a, option_b, option_c, option_d, correct)"
                    " VALUES (?, ?, 'A1', 'B1', 'C1', 'D1', 'b')",
                    (tid, f"Question number {i}"),
                ).lastrowid
            )
        db.commit()
        return tid, qids


