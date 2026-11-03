"""Aptitude tests: question bank (Admin), timed randomized attempts (Student), auto-grading.

Covers: FR12 (create tests / question bank), FR13 (timed attempt with auto-grade),
FR14 (randomized question order), FR15 (past scores), NFR3 (auto-save every 30 s),
SR7 / SE-09 (correct answers never sent to the browser before submission).
"""
import json
import random
from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, g, jsonify, redirect, render_template, request, url_for

from .charts import line_chart
from .db import get_db, log_action, utcnow
from .security import role_required

bp = Blueprint("aptitude", __name__)

GRACE_SECONDS = 5  # allowance for network delay when the timer hits zero


# ---------------------------------------------------------------- Admin: question bank
@bp.route("/admin/tests", methods=["GET", "POST"])
@role_required("admin")
def admin_tests():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        try:
            minutes = int(request.form.get("duration_minutes", ""))
            if not 1 <= minutes <= 180:
                raise ValueError
        except ValueError:
            minutes = None
        if not 3 <= len(title) <= 100 or minutes is None:
            flash("Title (3 to 100 characters) and duration (1 to 180 minutes) are required.", "error")
        else:
            cur = db.execute(
                "INSERT INTO tests (title, duration_minutes, created_by, created_at) VALUES (?, ?, ?, ?)",
                (title, minutes, g.user["id"], utcnow().isoformat()),
            )
            db.commit()
            log_action(g.user["id"], "TEST_CREATED", f"test_id={cur.lastrowid}")
            return redirect(url_for("aptitude.admin_test", test_id=cur.lastrowid))
    tests = db.execute(
        "SELECT t.*, (SELECT COUNT(*) FROM questions q WHERE q.test_id = t.id) AS n FROM tests t ORDER BY t.id DESC"
    ).fetchall()
    return render_template("admin_tests.html", tests=tests)


@bp.route("/admin/tests/<int:test_id>", methods=["GET", "POST"])
@role_required("admin")
def admin_test(test_id):
    db = get_db()
    test = db.execute("SELECT * FROM tests WHERE id = ?", (test_id,)).fetchone()
    if test is None:
        abort(404)
    if request.method == "POST":
        f = request.form
        text = f.get("text", "").strip()
        options = [f.get(f"option_{k}", "").strip() for k in "abcd"]
        correct = f.get("correct", "")
        if not text or len(text) > 500 or not all(options) or any(len(o) > 200 for o in options) or correct not in list("abcd"):
            flash("Enter the question, all four options (max 200 characters each) and the correct option.", "error")
        else:
            db.execute(
                "INSERT INTO questions (test_id, text, option_a, option_b, option_c, option_d, correct) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (test_id, text, *options, correct),
            )
            db.commit()
            flash("Question added.", "info")
        return redirect(url_for("aptitude.admin_test", test_id=test_id))
    questions = db.execute("SELECT * FROM questions WHERE test_id = ? ORDER BY id", (test_id,)).fetchall()
    return render_template("admin_test.html", test=test, questions=questions)


@bp.route("/admin/questions/<int:question_id>/delete", methods=["POST"])
@role_required("admin")
def delete_question(question_id):
    db = get_db()
    q = db.execute("SELECT test_id FROM questions WHERE id = ?", (question_id,)).fetchone()
    if q is None:
        abort(404)
    db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    db.commit()
    return redirect(url_for("aptitude.admin_test", test_id=q["test_id"]))


# ---------------------------------------------------------------- Student: attempts
@bp.route("/tests")
@role_required("student")
def tests():
    rows = get_db().execute(
        "SELECT t.*, (SELECT COUNT(*) FROM questions q WHERE q.test_id = t.id) AS n FROM tests t ORDER BY t.id DESC"
    ).fetchall()
    return render_template("tests.html", tests=rows)


@bp.route("/tests/<int:test_id>/start", methods=["POST"])
@role_required("student")
def start(test_id):
    db = get_db()
    test = db.execute("SELECT * FROM tests WHERE id = ?", (test_id,)).fetchone()
    if test is None:
        abort(404)
    ids = [r["id"] for r in db.execute("SELECT id FROM questions WHERE test_id = ?", (test_id,))]
    if not ids:
        flash("This test has no questions yet.", "error")
        return redirect(url_for("aptitude.tests"))
    open_attempt = db.execute(
        "SELECT id FROM attempts WHERE test_id = ? AND student_id = ? AND submitted_at IS NULL", (test_id, g.user["id"])
    ).fetchone()
    if open_attempt:  # resume instead of letting a student restart the clock
        return redirect(url_for("aptitude.attempt", attempt_id=open_attempt["id"]))
    random.shuffle(ids)  # FR14: a different random order for every attempt
    cur = db.execute(
        "INSERT INTO attempts (test_id, student_id, started_at, question_order) VALUES (?, ?, ?, ?)",
        (test_id, g.user["id"], utcnow().isoformat(), json.dumps(ids)),
    )
    db.commit()
    log_action(g.user["id"], "TEST_STARTED", f"attempt_id={cur.lastrowid}")
    return redirect(url_for("aptitude.attempt", attempt_id=cur.lastrowid))


def _own_attempt(attempt_id):
    row = get_db().execute(
        "SELECT a.*, t.title, t.duration_minutes FROM attempts a JOIN tests t ON t.id = a.test_id"
        " WHERE a.id = ? AND a.student_id = ?",
        (attempt_id, g.user["id"]),
    ).fetchone()
    if row is None:
        abort(404)
    return row


def _seconds_left(attempt):
    end = datetime.fromisoformat(attempt["started_at"]) + timedelta(minutes=attempt["duration_minutes"])
    return int((end - utcnow()).total_seconds())


def _grade_and_close(attempt, answers):
    db = get_db()
    order = json.loads(attempt["question_order"])
    correct = {r["id"]: r["correct"] for r in db.execute(
        f"SELECT id, correct FROM questions WHERE id IN ({','.join('?' * len(order))})", order)}
    score = sum(1 for qid in order if answers.get(str(qid)) == correct.get(qid))
    db.execute(
        "UPDATE attempts SET submitted_at = ?, score = ?, total = ?, answers = ? WHERE id = ?",
        (utcnow().isoformat(), score, len(order), json.dumps(answers), attempt["id"]),
    )
    db.commit()
    log_action(g.user["id"], "TEST_SUBMITTED", f"attempt_id={attempt['id']}, score={score}/{len(order)}")


def _collect_answers(form, order):
    valid = set(map(str, order))
    return {k[2:]: v for k, v in form.items() if k.startswith("q_") and k[2:] in valid and v in list("abcd")}


@bp.route("/attempts/<int:attempt_id>")
@role_required("student")
def attempt(attempt_id):
    a = _own_attempt(attempt_id)
    if a["submitted_at"]:
        return redirect(url_for("aptitude.result", attempt_id=attempt_id))
    left = _seconds_left(a)
    if left <= 0:  # time ran out while the student was away: auto-submit saved answers (alternate flow)
        _grade_and_close(a, json.loads(a["answers"]))
        flash("Time expired. Your saved answers were submitted automatically.", "info")
        return redirect(url_for("aptitude.result", attempt_id=attempt_id))
    order = json.loads(a["question_order"])
    by_id = {r["id"]: r for r in get_db().execute(
        f"SELECT id, text, option_a, option_b, option_c, option_d FROM questions WHERE id IN ({','.join('?' * len(order))})", order)}
    questions = [by_id[i] for i in order if i in by_id]  # note: the `correct` column is never selected here (SR7)
    return render_template("take_test.html", a=a, questions=questions, saved=json.loads(a["answers"]), seconds_left=left)


@bp.route("/attempts/<int:attempt_id>/save", methods=["POST"])
@role_required("student")
def save(attempt_id):
    """NFR3: called every 30 seconds by static/test.js so progress is never lost."""
    a = _own_attempt(attempt_id)
    if a["submitted_at"] or _seconds_left(a) <= -GRACE_SECONDS:
        return jsonify(saved=False), 409
    answers = _collect_answers(request.form, json.loads(a["question_order"]))
    get_db().execute("UPDATE attempts SET answers = ? WHERE id = ?", (json.dumps(answers), attempt_id))
    get_db().commit()
    return jsonify(saved=True, count=len(answers))


@bp.route("/attempts/<int:attempt_id>/submit", methods=["POST"])
@role_required("student")
def submit(attempt_id):
    a = _own_attempt(attempt_id)
    if not a["submitted_at"]:
        if _seconds_left(a) >= -GRACE_SECONDS:
            answers = _collect_answers(request.form, json.loads(a["question_order"]))
        else:  # too late: only what was auto-saved counts
            answers = json.loads(a["answers"])
        _grade_and_close(a, answers)
    return redirect(url_for("aptitude.result", attempt_id=attempt_id))


@bp.route("/attempts/<int:attempt_id>/result")
@role_required("student")
def result(attempt_id):
    a = _own_attempt(attempt_id)
    if not a["submitted_at"]:
        return redirect(url_for("aptitude.attempt", attempt_id=attempt_id))
    order = json.loads(a["question_order"])
    answers = json.loads(a["answers"])
    by_id = {r["id"]: r for r in get_db().execute(
        f"SELECT * FROM questions WHERE id IN ({','.join('?' * len(order))})", order)}
    review = [{"q": by_id[i], "chosen": answers.get(str(i))} for i in order if i in by_id]  # correct answers shown only now
    return render_template("result.html", a=a, review=review)


@bp.route("/scores")
@role_required("student")
def scores():
    """FR15: every finished attempt with test name, score and date, plus the trend chart."""
    rows = get_db().execute(
        "SELECT a.id, a.score, a.total, a.submitted_at, t.title FROM attempts a JOIN tests t ON t.id = a.test_id"
        " WHERE a.student_id = ? AND a.submitted_at IS NOT NULL ORDER BY a.submitted_at",
        (g.user["id"],),
    ).fetchall()
    chart = line_chart(
        [r["submitted_at"][5:10] for r in rows],
        [round(r["score"] / r["total"] * 100) for r in rows],
        title="Test score trend (%)",
    )
    return render_template("scores.html", rows=list(reversed(rows)), chart=chart)
