from tests.conftest import login, make_user, post
from tests.sprint2_helpers import *  # noqa: F401,F403  (shared setup helpers)
import io, json
from datetime import timedelta
from app.db import get_db, utcnow


# ------------------------------------------------------------------ FR12-FR15: aptitude tests
def test_admin_creates_test_and_questions(client, app):
    make_user(app, "admin@portal.local", "admin")
    login(client, "admin@portal.local")
    resp = post(client, "/admin/tests", {"title": "Logical Reasoning", "duration_minutes": "15"})
    assert resp.status_code == 302
    url = resp.headers["Location"]
    post(client, url, {"text": "2+2?", "option_a": "3", "option_b": "4", "option_c": "5", "option_d": "6", "correct": "b"})
    assert b"2+2?" in client.get(url).data


def test_question_needs_all_options(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, _ = make_test(app, admin, n_questions=0)
    login(client, "admin@portal.local")
    post(client, f"/admin/tests/{tid}", {"text": "Q?", "option_a": "1", "option_b": "", "option_c": "3", "option_d": "4", "correct": "a"})
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0


def test_student_cannot_manage_tests(client, app):
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    assert client.get("/admin/tests").status_code == 403


def test_correct_answers_are_never_sent_before_submission(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, _ = make_test(app, admin)
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    resp = post(client, f"/tests/{tid}/start")
    page = client.get(resp.headers["Location"]).data.decode()
    assert "Question number" in page
    assert "correct" not in page.lower() and "(correct)" not in page  # SR7


def test_question_order_is_a_random_permutation(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, qids = make_test(app, admin, n_questions=8)
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    orders = set()
    for _ in range(6):
        post(client, f"/tests/{tid}/start")
        with app.app_context():
            row = get_db().execute("SELECT id, question_order FROM attempts ORDER BY id DESC LIMIT 1").fetchone()
            order = json.loads(row["question_order"])
            assert sorted(order) == sorted(qids)
            orders.add(tuple(order))
            get_db().execute("UPDATE attempts SET submitted_at = ?, score = 0, total = 8 WHERE id = ?", (utcnow().isoformat(), row["id"]))
            get_db().commit()
    assert len(orders) > 1  # FR14


def test_submit_is_auto_graded(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, qids = make_test(app, admin, n_questions=4)  # every correct answer is 'b'
    sid = make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    post(client, f"/tests/{tid}/start")
    with app.app_context():
        aid = get_db().execute("SELECT id FROM attempts WHERE student_id = ?", (sid,)).fetchone()["id"]
    answers = {f"q_{qids[0]}": "b", f"q_{qids[1]}": "b", f"q_{qids[2]}": "a"}  # 2 right, 1 wrong, 1 blank
    resp = post(client, f"/attempts/{aid}/submit", answers)
    assert resp.status_code == 302
    with app.app_context():
        row = get_db().execute("SELECT score, total FROM attempts WHERE id = ?", (aid,)).fetchone()
    assert (row["score"], row["total"]) == (2, 4)
    result = client.get(f"/attempts/{aid}/result").data
    assert b"2 / 4" in result and b"(correct)" in result  # answers revealed only after submission


def test_autosave_stores_answers(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, qids = make_test(app, admin)
    sid = make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    post(client, f"/tests/{tid}/start")
    with app.app_context():
        aid = get_db().execute("SELECT id FROM attempts").fetchone()["id"]
    resp = post(client, f"/attempts/{aid}/save", {f"q_{qids[0]}": "c"})
    assert resp.get_json()["saved"] is True
    page = client.get(f"/attempts/{aid}").data.decode()
    assert "checked" in page  # the saved answer is restored when the page is reopened


def test_expired_attempt_is_auto_submitted_with_saved_answers(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, qids = make_test(app, admin, n_questions=2, minutes=5)
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    post(client, f"/tests/{tid}/start")
    with app.app_context():
        aid = get_db().execute("SELECT id FROM attempts").fetchone()["id"]
    post(client, f"/attempts/{aid}/save", {f"q_{qids[0]}": "b"})
    with app.app_context():  # pretend the student started 10 minutes ago
        get_db().execute("UPDATE attempts SET started_at = ? WHERE id = ?", ((utcnow() - timedelta(minutes=10)).isoformat(), aid))
        get_db().commit()
    resp = client.get(f"/attempts/{aid}")
    assert resp.status_code == 302 and "result" in resp.headers["Location"]
    with app.app_context():
        row = get_db().execute("SELECT score, submitted_at FROM attempts WHERE id = ?", (aid,)).fetchone()
    assert row["submitted_at"] and row["score"] == 1


def test_late_submit_only_counts_saved_answers(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, qids = make_test(app, admin, n_questions=2, minutes=5)
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    post(client, f"/tests/{tid}/start")
    with app.app_context():
        aid = get_db().execute("SELECT id FROM attempts").fetchone()["id"]
        get_db().execute("UPDATE attempts SET started_at = ? WHERE id = ?", ((utcnow() - timedelta(minutes=30)).isoformat(), aid))
        get_db().commit()
    post(client, f"/attempts/{aid}/submit", {f"q_{qids[0]}": "b", f"q_{qids[1]}": "b"})  # sent far too late
    with app.app_context():
        assert get_db().execute("SELECT score FROM attempts WHERE id = ?", (aid,)).fetchone()["score"] == 0


def test_student_cannot_open_another_students_attempt(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, _ = make_test(app, admin)
    make_user(app, "s1@pes.edu", "student")
    make_user(app, "s2@pes.edu", "student")
    login(client, "s1@pes.edu")
    post(client, f"/tests/{tid}/start")
    with app.app_context():
        aid = get_db().execute("SELECT id FROM attempts").fetchone()["id"]
    logout(client)
    login(client, "s2@pes.edu")
    assert client.get(f"/attempts/{aid}").status_code == 404
    assert post(client, f"/attempts/{aid}/submit").status_code == 404


def test_restarting_resumes_the_open_attempt(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, _ = make_test(app, admin)
    make_user(app, "s@pes.edu", "student")
    login(client, "s@pes.edu")
    first = post(client, f"/tests/{tid}/start").headers["Location"]
    second = post(client, f"/tests/{tid}/start").headers["Location"]
    assert first == second


def test_scores_page_lists_attempts_with_chart(client, app):
    admin = make_user(app, "admin@portal.local", "admin")
    tid, qids = make_test(app, admin, n_questions=2)
    sid = make_user(app, "s@pes.edu", "student")
    with app.app_context():
        for score in (1, 2):
            get_db().execute(
                "INSERT INTO attempts (test_id, student_id, started_at, submitted_at, score, total, question_order, answers)"
                " VALUES (?, ?, ?, ?, ?, 2, '[]', '{}')",
                (tid, sid, utcnow().isoformat(), utcnow().isoformat(), score),
            )
        get_db().commit()
    login(client, "s@pes.edu")
    page = client.get("/scores").data
    assert b"Quant 1" in page and b"1 / 2" in page and b"2 / 2" in page and b"<polyline" in page


