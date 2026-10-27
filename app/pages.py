"""Landing redirect and the role-specific dashboards."""
from flask import Blueprint, g, redirect, render_template, url_for

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
    return render_template("recruiter.html")
