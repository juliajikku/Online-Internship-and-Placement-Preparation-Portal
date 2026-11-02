"""Applying, status tracking, recruiter review and offer acceptance.

Covers: FR7/FR8 (apply only if eligible, using saved profile and resume),
FR9/FR10 (status tracking and recruiter updates), FR11 (auto-close other
applications when an offer is accepted), SE-06 (audit log).
"""
from datetime import date

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from .db import get_db, log_action, utcnow
from .listings import eligibility
from .profiles import get_student_profile
from .security import role_required

bp = Blueprint("applications", __name__)

STATUSES = ["Applied", "Shortlisted", "Test", "Interview", "Offered", "Rejected"]
FINAL = ("Rejected", "Accepted", "Closed")  # no further recruiter changes


@bp.route("/listings/<int:listing_id>/apply", methods=["POST"])
@role_required("student")
def apply(listing_id):
    db = get_db()
    listing = db.execute(
        "SELECT l.*, u.status AS recruiter_status FROM listings l JOIN users u ON u.id = l.recruiter_id WHERE l.id = ?",
        (listing_id,),
    ).fetchone()
    if listing is None or listing["recruiter_status"] != "active" or listing["deadline"] < date.today().isoformat():
        abort(404)
    unmet = eligibility(get_student_profile(g.user["id"]), listing)
    if unmet:  # the server re-checks even though the button is disabled in the page (FR7)
        flash("You cannot apply: " + " ".join(unmet), "error")
        return redirect(url_for("listings.browse"))
    if db.execute("SELECT 1 FROM applications WHERE listing_id = ? AND student_id = ?", (listing_id, g.user["id"])).fetchone():
        flash("You have already applied to this listing.", "error")
        return redirect(url_for("applications.mine"))
    now = utcnow().isoformat()
    cur = db.execute(
        "INSERT INTO applications (listing_id, student_id, status, applied_at, updated_at) VALUES (?, ?, 'Applied', ?, ?)",
        (listing_id, g.user["id"], now, now),
    )
    db.commit()
    log_action(g.user["id"], "APPLICATION_SUBMITTED", f"application_id={cur.lastrowid}")
    # Deviation: the confirmation email is only logged (no mail server in the demo).
    current_app.logger.info("Confirmation email would be sent to %s for listing %s", g.user["email"], listing_id)
    flash("Application submitted. A confirmation would be emailed to you.", "info")
    return redirect(url_for("applications.mine"))


@bp.route("/applications")
@role_required("student")
def mine():
    rows = get_db().execute(
        "SELECT a.*, l.role, l.stipend, u.company_name FROM applications a"
        " JOIN listings l ON l.id = a.listing_id JOIN users u ON u.id = l.recruiter_id"
        " WHERE a.student_id = ? ORDER BY a.applied_at DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("my_applications.html", rows=rows)


@bp.route("/applications/<int:application_id>/accept", methods=["POST"])
@role_required("student")
def accept_offer(application_id):
    """FR11: accepting an offer closes all of the student's other open applications."""
    db = get_db()
    app_row = db.execute(
        "SELECT * FROM applications WHERE id = ? AND student_id = ?", (application_id, g.user["id"])
    ).fetchone()
    if app_row is None:
        abort(404)
    if app_row["status"] != "Offered":
        flash("Only an application with an offer can be accepted.", "error")
        return redirect(url_for("applications.mine"))
    now = utcnow().isoformat()
    db.execute("UPDATE applications SET status = 'Accepted', updated_at = ? WHERE id = ?", (now, application_id))
    closed = db.execute(
        "UPDATE applications SET status = 'Closed', updated_at = ?"
        " WHERE student_id = ? AND id != ? AND status NOT IN ('Rejected', 'Accepted', 'Closed')",
        (now, g.user["id"], application_id),
    ).rowcount
    db.commit()
    log_action(g.user["id"], "OFFER_ACCEPTED", f"application_id={application_id}, closed_others={closed}")
    flash(f"Offer accepted. You are marked Placed and {closed} other application(s) were closed.", "info")
    return redirect(url_for("applications.mine"))


def _own_listing(listing_id):
    listing = get_db().execute(
        "SELECT * FROM listings WHERE id = ? AND recruiter_id = ?", (listing_id, g.user["id"])
    ).fetchone()
    if listing is None:
        abort(404)  # not found or not yours: recruiters never see other recruiters' listings
    return listing


@bp.route("/recruiter/listings/<int:listing_id>/applicants")
@role_required("recruiter")
def applicants(listing_id):
    listing = _own_listing(listing_id)
    rows = get_db().execute(
        "SELECT a.*, u.name, u.email, p.cgpa, p.branch, p.skills, p.resume_file,"
        " (SELECT MAX(CAST(t.score AS REAL) / t.total * 100) FROM attempts t"
        "   WHERE t.student_id = a.student_id AND t.submitted_at IS NOT NULL) AS best_score"
        " FROM applications a JOIN users u ON u.id = a.student_id"
        " LEFT JOIN student_profiles p ON p.user_id = a.student_id"
        " WHERE a.listing_id = ? ORDER BY a.applied_at",
        (listing_id,),
    ).fetchall()
    return render_template("applicants.html", listing=listing, rows=rows, statuses=STATUSES, final=FINAL)


@bp.route("/recruiter/applications/<int:application_id>/status", methods=["POST"])
@role_required("recruiter")
def update_status(application_id):
    db = get_db()
    row = db.execute(
        "SELECT a.* FROM applications a JOIN listings l ON l.id = a.listing_id"
        " WHERE a.id = ? AND l.recruiter_id = ?",
        (application_id, g.user["id"]),
    ).fetchone()
    if row is None:
        abort(404)
    new_status = request.form.get("status", "")
    if new_status not in STATUSES:
        abort(400)
    if row["status"] in FINAL:
        flash(f"This application is {row['status']} and can no longer be changed.", "error")
    else:
        db.execute("UPDATE applications SET status = ?, updated_at = ? WHERE id = ?", (new_status, utcnow().isoformat(), application_id))
        db.commit()
        log_action(g.user["id"], "STATUS_UPDATED", f"application_id={application_id}, status={new_status}")
        flash(f"Status changed to {new_status}. The student would be notified by email.", "info")
    return redirect(url_for("applications.applicants", listing_id=row["listing_id"]))
