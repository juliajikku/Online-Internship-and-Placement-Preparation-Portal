from tests.conftest import login, make_user, post
from tests.sprint2_helpers import *  # noqa: F401,F403  (shared setup helpers)
import io, json
from datetime import timedelta
from app.db import get_db, utcnow


# ------------------------------------------------------------------ FR2 / SR6: student profile + resume
def test_student_saves_profile_with_valid_pdf(client, app):
    sid = make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    resp = upload(client, "/student/profile", {"cgpa": "8.2", "branch": "CSE", "skills": "Python"}, (io.BytesIO(PDF), "cv.pdf"))
    assert resp.status_code == 302
    with app.app_context():
        row = get_db().execute("SELECT * FROM student_profiles WHERE user_id = ?", (sid,)).fetchone()
    assert row["cgpa"] == 8.2 and row["resume_name"] == "cv.pdf" and row["resume_file"].endswith(".pdf")


def test_saved_profile_page_reopens_with_values(client, app):
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid, cgpa=8.4, branch="CSE")
    login(client, "s@pes.edu")
    page = client.get("/student/profile")
    assert page.status_code == 200 and b"8.4" in page.data and b"r.pdf" in page.data


def test_resume_with_wrong_type_is_rejected(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    resp = upload(client, "/student/profile", {"cgpa": "8", "branch": "CSE"}, (io.BytesIO(b"MZ binary"), "setup.exe"))
    assert resp.status_code == 400 and b"Only PDF or DOCX" in resp.data


def test_resume_over_5mb_is_rejected(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    big = PDF + b"0" * (5 * 1024 * 1024 + 10)
    resp = upload(client, "/student/profile", {"cgpa": "8", "branch": "CSE"}, (io.BytesIO(big), "big.pdf"))
    assert resp.status_code == 400 and b"5 MB" in resp.data


def test_fake_pdf_content_is_rejected(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    resp = upload(client, "/student/profile", {"cgpa": "8", "branch": "CSE"}, (io.BytesIO(b"just text"), "fake.pdf"))
    assert resp.status_code == 400


def test_invalid_cgpa_rejected(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    assert post(client, "/student/profile", {"cgpa": "12", "branch": "CSE"}).status_code == 400


def test_recruiter_cannot_open_student_profile(client, app):
    make_user(app, "r@acme.com", "recruiter", company="Acme")
    login(client, "r@acme.com")
    assert client.get("/student/profile").status_code == 403


# ------------------------------------------------------------------ FR3: recruiter profile
def test_recruiter_updates_company_profile(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    login(client, "r@acme.com")
    resp = post(client, "/recruiter/profile", {"company_name": "Acme Labs", "description": "We build", "website": "https://acme.com"})
    assert resp.status_code == 302
    with app.app_context():
        assert get_db().execute("SELECT company_name FROM users WHERE id = ?", (rid,)).fetchone()[0] == "Acme Labs"


def test_company_website_must_be_http(client, app):
    make_user(app, "r@acme.com", "recruiter", company="Acme")
    login(client, "r@acme.com")
    assert post(client, "/recruiter/profile", {"company_name": "Acme", "website": "javascript:alert(1)"}).status_code == 400


# ------------------------------------------------------------------ FR5: posting listings
LISTING_FORM = {"role": "Backend Intern", "domain": "Software", "location": "Pune", "min_cgpa": "7.5",
                "branches": "CSE, ISE", "stipend": "15000", "deadline": FUTURE, "description": "Build APIs"}


def test_approved_recruiter_can_post_listing(client, app):
    make_user(app, "r@acme.com", "recruiter", company="Acme")
    login(client, "r@acme.com")
    assert post(client, "/recruiter/listings", LISTING_FORM).status_code == 302
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM listings").fetchone()[0] == 1


def test_pending_recruiter_cannot_post_listing(client, app):
    make_user(app, "r@acme.com", "recruiter", status="pending", company="Acme")
    login(client, "r@acme.com")
    post(client, "/recruiter/listings", LISTING_FORM)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM listings").fetchone()[0] == 0


def test_listing_requires_all_criteria(client, app):
    make_user(app, "r@acme.com", "recruiter", company="Acme")
    login(client, "r@acme.com")
    for missing in ("role", "min_cgpa", "stipend", "deadline"):
        form = dict(LISTING_FORM, **{missing: ""})
        assert post(client, "/recruiter/listings", form).status_code == 400, missing


def test_listing_deadline_in_past_rejected(client, app):
    make_user(app, "r@acme.com", "recruiter", company="Acme")
    login(client, "r@acme.com")
    assert post(client, "/recruiter/listings", dict(LISTING_FORM, deadline=PAST)).status_code == 400


def test_student_cannot_post_listing(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    assert client.get("/recruiter/listings").status_code == 403


# ------------------------------------------------------------------ FR6: search and filter
def test_students_only_see_active_unexpired_listings(client, app):
    ok = make_user(app, "r@acme.com", "recruiter", company="Acme")
    pend = make_user(app, "p@x.com", "recruiter", status="pending", company="Pending Co")
    add_listing(app, ok, role="Visible Role")
    add_listing(app, ok, role="Expired Role", deadline=PAST)
    add_listing(app, pend, role="Unapproved Role")
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    page = client.get("/listings").data
    assert b"Visible Role" in page and b"Expired Role" not in page and b"Unapproved Role" not in page


def test_filters_can_be_combined(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    add_listing(app, rid, role="Web Dev", domain="Software", location="Bengaluru", stipend=25000)
    add_listing(app, rid, role="Data Analyst", domain="Data Science", location="Bengaluru", stipend=10000)
    add_listing(app, rid, role="Embedded Eng", domain="Electronics", location="Pune", stipend=30000)
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    page = client.get("/listings?domain=Software&location=Beng&min_stipend=20000").data
    assert b"Web Dev" in page and b"Data Analyst" not in page and b"Embedded Eng" not in page
    assert b"Data Analyst" in client.get("/listings?q=analyst").data


# ------------------------------------------------------------------ FR7 / FR8: eligibility and apply
def test_eligible_student_can_apply(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid, min_cgpa=7.0, branches="CSE")
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid, cgpa=8.0, branch="cse")
    login(client, "s@pes.edu")
    assert post(client, f"/listings/{lid}/apply").status_code == 302
    with app.app_context():
        row = get_db().execute("SELECT status FROM applications WHERE student_id = ?", (sid,)).fetchone()
    assert row["status"] == "Applied"


def test_ineligible_cgpa_is_blocked_and_reason_shown(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid, min_cgpa=8.0)
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid, cgpa=6.0)
    login(client, "s@pes.edu")
    page = client.get("/listings").data
    assert b"below the minimum" in page and b"disabled" in page  # Apply button disabled with reason
    post(client, f"/listings/{lid}/apply")  # even a forged request is refused by the server
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM applications").fetchone()[0] == 0


def test_wrong_branch_is_blocked(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid, branches="ECE")
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid, branch="CSE")
    login(client, "s@pes.edu")
    post(client, f"/listings/{lid}/apply")
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM applications").fetchone()[0] == 0


def test_cannot_apply_without_resume(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid)
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid, resume=False)
    login(client, "s@pes.edu")
    post(client, f"/listings/{lid}/apply")
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM applications").fetchone()[0] == 0


def test_cannot_apply_twice(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid)
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid)
    login(client, "s@pes.edu")
    post(client, f"/listings/{lid}/apply")
    post(client, f"/listings/{lid}/apply")
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM applications").fetchone()[0] == 1


def test_cannot_apply_to_expired_listing(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid, deadline=PAST)
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid)
    login(client, "s@pes.edu")
    assert post(client, f"/listings/{lid}/apply").status_code == 404


def test_application_is_written_to_audit_log(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid)
    sid = make_user(app, "s@pes.edu", "student")
    set_profile(app, sid)
    login(client, "s@pes.edu")
    post(client, f"/listings/{lid}/apply")
    with app.app_context():
        assert "APPLICATION_SUBMITTED" in [r[0] for r in get_db().execute("SELECT action FROM audit_log")]


# ------------------------------------------------------------------ FR9 / FR10: recruiter review
def test_recruiter_updates_status_and_student_sees_it(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    lid = add_listing(app, rid)
    sid = make_user(app, "s@pes.edu", "student")
    aid = add_application(app, lid, sid)
    login(client, "r@acme.com")
    assert b"s@pes.edu" in client.get(f"/recruiter/listings/{lid}/applicants").data
    post(client, f"/recruiter/applications/{aid}/status", {"status": "Shortlisted"})
    assert app_status(app, aid) == "Shortlisted"
    logout(client)
    login(client, "s@pes.edu")
    assert b"Shortlisted" in client.get("/applications").data


def test_recruiter_cannot_see_other_recruiters_applicants(client, app):
    r1 = make_user(app, "r1@acme.com", "recruiter", company="Acme")
    make_user(app, "r2@beta.com", "recruiter", company="Beta")
    lid = add_listing(app, r1)
    sid = make_user(app, "s@pes.edu", "student")
    aid = add_application(app, lid, sid)
    login(client, "r2@beta.com")
    assert client.get(f"/recruiter/listings/{lid}/applicants").status_code == 404
    assert post(client, f"/recruiter/applications/{aid}/status", {"status": "Offered"}).status_code == 404
    assert app_status(app, aid) == "Applied"


def test_invalid_status_value_rejected(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    aid = add_application(app, add_listing(app, rid), make_user(app, "s@pes.edu", "student"))
    login(client, "r@acme.com")
    assert post(client, f"/recruiter/applications/{aid}/status", {"status": "Hired!!"}).status_code == 400


def test_final_statuses_cannot_be_changed(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    aid = add_application(app, add_listing(app, rid), make_user(app, "s@pes.edu", "student"), status="Rejected")
    login(client, "r@acme.com")
    post(client, f"/recruiter/applications/{aid}/status", {"status": "Offered"})
    assert app_status(app, aid) == "Rejected"


def test_student_cannot_update_status(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    sid = make_user(app, "s@pes.edu", "student")
    aid = add_application(app, add_listing(app, rid), sid)
    login(client, "s@pes.edu")
    assert post(client, f"/recruiter/applications/{aid}/status", {"status": "Offered"}).status_code == 403


# ------------------------------------------------------------------ FR11: accept offer closes others
def test_accepting_offer_closes_other_open_applications(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    sid = make_user(app, "s@pes.edu", "student")
    offer = add_application(app, add_listing(app, rid, role="A"), sid, status="Offered")
    other1 = add_application(app, add_listing(app, rid, role="B"), sid, status="Applied")
    other2 = add_application(app, add_listing(app, rid, role="C"), sid, status="Interview")
    rejected = add_application(app, add_listing(app, rid, role="D"), sid, status="Rejected")
    login(client, "s@pes.edu")
    post(client, f"/applications/{offer}/accept")
    assert app_status(app, offer) == "Accepted"
    assert app_status(app, other1) == "Closed" and app_status(app, other2) == "Closed"
    assert app_status(app, rejected) == "Rejected"  # already final, left alone


def test_cannot_accept_without_an_offer(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    sid = make_user(app, "s@pes.edu", "student")
    aid = add_application(app, add_listing(app, rid), sid, status="Applied")
    login(client, "s@pes.edu")
    post(client, f"/applications/{aid}/accept")
    assert app_status(app, aid) == "Applied"


def test_cannot_accept_someone_elses_offer(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    s1 = make_user(app, "s1@pes.edu", "student")
    make_user(app, "s2@pes.edu", "student")
    aid = add_application(app, add_listing(app, rid), s1, status="Offered")
    login(client, "s2@pes.edu")
    assert post(client, f"/applications/{aid}/accept").status_code == 404


# ------------------------------------------------------------------ resume download access
def test_resume_access_rules(client, app):
    rid = make_user(app, "r@acme.com", "recruiter", company="Acme")
    other = make_user(app, "r2@beta.com", "recruiter", company="Beta")
    s1 = make_user(app, "s1@pes.edu", "student")
    make_user(app, "s2@pes.edu", "student")
    login(client, "s1@pes.edu")
    upload(client, "/student/profile", {"cgpa": "8", "branch": "CSE"}, (io.BytesIO(PDF), "cv.pdf"))
    assert client.get(f"/resume/{s1}").status_code == 200  # owner
    logout(client)
    login(client, "s2@pes.edu")
    assert client.get(f"/resume/{s1}").status_code == 403  # another student
    logout(client)
    add_application(app, add_listing(app, rid), s1)
    login(client, "r@acme.com")
    assert client.get(f"/resume/{s1}").status_code == 200  # recruiter who received the application
    logout(client)
    login(client, "r2@beta.com")
    assert client.get(f"/resume/{s1}").status_code == 403  # unrelated recruiter


