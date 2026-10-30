"""Student and recruiter profiles, resume upload and download.

Covers: FR2 (student profile + resume), FR3 (recruiter company profile),
SE-08 / SR6 (resume must be PDF or DOCX and at most 5 MB).
"""
import os
import uuid

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, send_from_directory, url_for

from .db import get_db, log_action, utcnow
from .security import login_required, role_required

bp = Blueprint("profiles", __name__)

MAX_RESUME_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf": b"%PDF", ".docx": b"PK"}  # extension -> required first bytes


def get_student_profile(user_id):
    return get_db().execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()


def profile_is_complete(profile):
    return bool(profile and profile["resume_file"])


def _save_resume(file_storage):
    """Validate and store an uploaded resume. Returns (stored_name, original_name) or raises ValueError."""
    original = os.path.basename(file_storage.filename or "")
    ext = os.path.splitext(original)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF or DOCX files are allowed.")
    data = file_storage.read(MAX_RESUME_BYTES + 1)
    if len(data) > MAX_RESUME_BYTES:
        raise ValueError("Resume must be 5 MB or smaller.")
    if not data.startswith(ALLOWED_EXTENSIONS[ext]):
        raise ValueError("The file content does not match a real PDF or DOCX file.")
    stored = f"{uuid.uuid4().hex}{ext}"  # random name: the user's filename is never used on disk
    os.makedirs(current_app.config["UPLOAD_DIR"], exist_ok=True)
    with open(os.path.join(current_app.config["UPLOAD_DIR"], stored), "wb") as fh:
        fh.write(data)
    return stored, original[:120]


@bp.route("/student/profile", methods=["GET", "POST"])
@role_required("student")
def student_profile():
    db = get_db()
    profile = get_student_profile(g.user["id"])
    if request.method == "POST":
        errors = []
        try:
            cgpa = float(request.form.get("cgpa", ""))
            if not 0 <= cgpa <= 10:
                raise ValueError
        except ValueError:
            errors.append("CGPA must be a number between 0 and 10.")
            cgpa = None
        branch = request.form.get("branch", "").strip()
        skills = request.form.get("skills", "").strip()
        if not 2 <= len(branch) <= 40:
            errors.append("Branch must be 2 to 40 characters (for example CSE).")
        if len(skills) > 300:
            errors.append("Skills must be 300 characters or fewer.")

        resume_file = profile["resume_file"] if profile else None
        resume_name = profile["resume_name"] if profile else None
        upload = request.files.get("resume")
        if upload and upload.filename:
            try:
                resume_file, resume_name = _save_resume(upload)
            except ValueError as exc:
                errors.append(str(exc))
        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("student_profile.html", profile=request.form, current=profile), 400

        db.execute(
            "INSERT INTO student_profiles (user_id, cgpa, branch, skills, resume_file, resume_name, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(user_id) DO UPDATE SET cgpa=excluded.cgpa, branch=excluded.branch,"
            " skills=excluded.skills, resume_file=excluded.resume_file, resume_name=excluded.resume_name,"
            " updated_at=excluded.updated_at",
            (g.user["id"], cgpa, branch, skills, resume_file, resume_name, utcnow().isoformat()),
        )
        db.commit()
        log_action(g.user["id"], "PROFILE_UPDATED")
        flash("Profile saved.", "info")
        return redirect(url_for("profiles.student_profile"))
    return render_template("student_profile.html", profile=dict(profile) if profile else {}, current=profile)


@bp.route("/recruiter/profile", methods=["GET", "POST"])
@role_required("recruiter")
def recruiter_profile():
    db = get_db()
    profile = db.execute("SELECT * FROM recruiter_profiles WHERE user_id = ?", (g.user["id"],)).fetchone()
    if request.method == "POST":
        company = request.form.get("company_name", "").strip()
        description = request.form.get("description", "").strip()
        website = request.form.get("website", "").strip()
        errors = []
        if not 2 <= len(company) <= 100:
            errors.append("Company name must be 2 to 100 characters.")
        if len(description) > 1000:
            errors.append("Description must be 1000 characters or fewer.")
        if website and not (website.startswith(("http://", "https://")) and len(website) <= 200):
            errors.append("Website must start with http:// or https://.")
        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("recruiter_profile.html", profile=request.form), 400
        db.execute("UPDATE users SET company_name = ? WHERE id = ?", (company, g.user["id"]))
        db.execute(
            "INSERT INTO recruiter_profiles (user_id, description, website, updated_at) VALUES (?, ?, ?, ?)"
            " ON CONFLICT(user_id) DO UPDATE SET description=excluded.description,"
            " website=excluded.website, updated_at=excluded.updated_at",
            (g.user["id"], description, website, utcnow().isoformat()),
        )
        db.commit()
        log_action(g.user["id"], "COMPANY_PROFILE_UPDATED")
        flash("Company profile saved.", "info")
        return redirect(url_for("profiles.recruiter_profile"))
    data = {"company_name": g.user["company_name"], **(dict(profile) if profile else {})}
    return render_template("recruiter_profile.html", profile=data)


@bp.route("/resume/<int:student_id>")
@login_required
def resume(student_id):
    """Only the owner, the Admin, or a recruiter who received an application from this student may download."""
    allowed = g.user["id"] == student_id or g.user["role"] == "admin"
    if not allowed and g.user["role"] == "recruiter":
        allowed = bool(
            get_db()
            .execute(
                "SELECT 1 FROM applications a JOIN listings l ON l.id = a.listing_id"
                " WHERE a.student_id = ? AND l.recruiter_id = ?",
                (student_id, g.user["id"]),
            )
            .fetchone()
        )
    if not allowed:
        abort(403)
    profile = get_student_profile(student_id)
    if not profile or not profile["resume_file"]:
        abort(404)
    return send_from_directory(
        current_app.config["UPLOAD_DIR"], profile["resume_file"], as_attachment=True, download_name=profile["resume_name"]
    )
