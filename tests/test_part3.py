from tests.conftest import login, make_user, post
from tests.sprint2_helpers import *  # noqa: F401,F403  (shared setup helpers)
import io, json
from datetime import timedelta
from app.db import get_db, utcnow


# ------------------------------------------------------------------ analytics, charts, CSV
def test_student_dashboard_shows_charts_and_counts(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    sid = make_user(app, "s@pes.edu", "student")
    add_application(app, add_listing(app, rid, role="A"), sid, status="Shortlisted")
    add_application(app, add_listing(app, rid, role="B"), sid, status="Offered")
    login(client, "s@pes.edu")
    page = client.get("/student").data
    assert b"<svg" in page and b"My applications by status" in page and b"Shortlisted" in page


def test_admin_analytics_numbers(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    s1 = make_user(app, "s1@pes.edu", "student")
    make_user(app, "s2@pes.edu", "student")
    add_application(app, add_listing(app, rid), s1, status="Accepted")
    login(client, "admin@portal.local")
    page = client.get("/admin/analytics").data.decode()
    assert "50.0%" in page  # 1 of 2 students placed
    assert "Applications by status" in page and "Top companies by offers" in page and "Acme" in page


def test_student_cannot_open_admin_analytics_or_report(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    assert client.get("/admin/analytics").status_code == 403
    assert client.get("/admin/report.csv").status_code == 403


def test_admin_can_download_csv_report(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    sid = make_user(app, "s@pes.edu", "student", name="Asha Rao")
    set_profile(app, sid)
    add_application(app, add_listing(app, rid), sid, status="Offered")
    login(client, "admin@portal.local")
    resp = client.get("/admin/report.csv")
    assert resp.status_code == 200 and resp.mimetype == "text/csv"
    text = resp.data.decode()
    assert text.splitlines()[0].startswith("Student,Email") and "Asha Rao" in text and "Offered" in text


def test_csv_neutralises_formula_injection(client, app):
    make_user(app, "admin@portal.local", "admin")
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    sid = make_user(app, "s@pes.edu", "student", name="=HYPERLINK(\"http://evil\")")
    add_application(app, add_listing(app, rid), sid)
    login(client, "admin@portal.local")
    assert "'=HYPERLINK" in client.get("/admin/report.csv").data.decode()


def test_charts_handle_empty_data():
    from app.charts import bar_chart, donut_chart, line_chart

    assert "No test attempts yet" in line_chart([], [])
    assert "No data yet" in bar_chart([], title="x") and "No data yet" in donut_chart([], title="x")


def test_chart_labels_are_escaped():
    from app.charts import bar_chart

    assert "<script>" not in bar_chart([("<script>alert(1)</script>", 3)], title="t")
