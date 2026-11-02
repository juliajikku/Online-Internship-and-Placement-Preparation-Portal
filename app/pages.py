"""Landing redirect and the role-specific dashboards."""
from flask import Blueprint, g, redirect, render_template, url_for

from .db import get_db
from .security import login_required, role_required

bp = Blueprint("pages", __name__)


@bp.route("/")
def index():
    if g.user is None:
        return redirect(url_for("auth.login"))
    return redirect(url_for("pages.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    """Send each role to its own dashboard after login (use case step 3-4)."""
    target = {
        "student": "pages.student_home",
        "recruiter": "pages.recruiter_home",
        "admin": "admin.queue",
    }[g.user["role"]]
    return redirect(url_for(target))


@bp.route("/student")
@role_required("student")
def student_home():
    return render_template("student.html")


@bp.route("/recruiter")
@role_required("recruiter")
def recruiter_home():
    listings = get_db().execute(
        "SELECT COUNT(*) FROM listings WHERE recruiter_id = ?", (g.user["id"],)
    ).fetchone()[0]
    applicants = get_db().execute(
        "SELECT COUNT(*) FROM applications a JOIN listings l ON l.id = a.listing_id WHERE l.recruiter_id = ?",
        (g.user["id"],),
    ).fetchone()[0]
    return render_template("recruiter.html", listings=listings, applicants=applicants)
