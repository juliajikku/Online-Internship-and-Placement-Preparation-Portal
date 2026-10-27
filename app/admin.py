"""Admin approval of recruiter accounts (US-07, FR4)."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for

from .db import get_db, log_action
from .security import role_required
from flask import g

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@role_required("admin")
def queue():
    db = get_db()
    pending = db.execute(
        "SELECT id, name, email, company_name, created_at FROM users"
        " WHERE role = 'recruiter' AND status = 'pending' ORDER BY created_at"
    ).fetchall()
    decided = db.execute(
        "SELECT id, name, email, company_name, status FROM users"
        " WHERE role = 'recruiter' AND status IN ('active', 'rejected') ORDER BY name"
    ).fetchall()
    return render_template("admin.html", pending=pending, decided=decided)


def _decide(recruiter_id, new_status, action):
    db = get_db()
    recruiter = db.execute(
        "SELECT id, status FROM users WHERE id = ? AND role = 'recruiter'", (recruiter_id,)
    ).fetchone()
    if recruiter is None:
        abort(404)
    if recruiter["status"] != "pending":
        flash("That recruiter has already been reviewed.", "error")
        return redirect(url_for("admin.queue"))
    db.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, recruiter_id))
    db.commit()
    log_action(g.user["id"], action, f"recruiter_id={recruiter_id}")
    flash(f"Recruiter {new_status}.", "info")
    return redirect(url_for("admin.queue"))


@bp.route("/recruiters/<int:recruiter_id>/approve", methods=["POST"])
@role_required("admin")
def approve(recruiter_id):
    return _decide(recruiter_id, "active", "RECRUITER_APPROVED")


@bp.route("/recruiters/<int:recruiter_id>/reject", methods=["POST"])
@role_required("admin")
def reject(recruiter_id):
    return _decide(recruiter_id, "rejected", "RECRUITER_REJECTED")
