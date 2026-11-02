"""Internship listings: recruiters post them, students search and filter them.

Covers: FR5 (post listings with eligibility criteria), FR6 (search and filter),
FR7 (eligibility check used to disable Apply).
"""
from datetime import date

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .db import get_db, log_action, utcnow
from .profiles import get_student_profile
from .security import role_required

bp = Blueprint("listings", __name__)

DOMAINS = ["Software", "Data Science", "Electronics", "Mechanical", "Design", "Other"]


def eligibility(profile, listing):
    """Return a list of unmet criteria (empty list means eligible)."""
    if profile is None:
        return ["Complete your student profile (CGPA, branch) first."]
    reasons = []
    if profile["cgpa"] < listing["min_cgpa"]:
        reasons.append(f"CGPA {profile['cgpa']:.2f} is below the minimum {listing['min_cgpa']:.2f}.")
    allowed = [b.strip().lower() for b in (listing["branches"] or "").split(",") if b.strip()]
    if allowed and profile["branch"].strip().lower() not in allowed:
        reasons.append(f"Branch {profile['branch']} is not accepted (allowed: {listing['branches']}).")
    if not profile["resume_file"]:
        reasons.append("Upload your resume in your profile first.")
    return reasons


def visible_listings_query():
    """Listings students may see: approved recruiter, deadline not passed."""
    return (
        "SELECT l.*, u.company_name FROM listings l JOIN users u ON u.id = l.recruiter_id"
        " WHERE u.status = 'active' AND l.deadline >= ?"
    )


@bp.route("/listings")
@role_required("student")
def browse():
    q = request.args.get("q", "").strip()[:80]
    domain = request.args.get("domain", "")
    location = request.args.get("location", "").strip()[:80]
    min_stipend = request.args.get("min_stipend", "").strip()

    sql = visible_listings_query()
    params = [date.today().isoformat()]
    if q:
        sql += " AND (l.role LIKE ? OR u.company_name LIKE ? OR l.description LIKE ?)"
        params += [f"%{q}%"] * 3
    if domain in DOMAINS:
        sql += " AND l.domain = ?"
        params.append(domain)
    if location:
        sql += " AND l.location LIKE ?"
        params.append(f"%{location}%")
    if min_stipend.isdigit():
        sql += " AND l.stipend >= ?"
        params.append(int(min_stipend))
    sql += " ORDER BY l.deadline"

    db = get_db()
    profile = get_student_profile(g.user["id"])
    applied = {r["listing_id"] for r in db.execute("SELECT listing_id FROM applications WHERE student_id = ?", (g.user["id"],))}
    rows = []
    for listing in db.execute(sql, params).fetchall():
        rows.append({"l": listing, "unmet": eligibility(profile, listing), "applied": listing["id"] in applied})
    return render_template(
        "listings.html", rows=rows, domains=DOMAINS, filters={"q": q, "domain": domain, "location": location, "min_stipend": min_stipend}
    )


@bp.route("/recruiter/listings", methods=["GET", "POST"])
@role_required("recruiter")
def manage():
    db = get_db()
    approved = g.user["status"] == "active"
    if request.method == "POST":
        if not approved:
            flash("Your account must be approved by the Admin before you can post listings.", "error")
            return redirect(url_for("listings.manage"))
        f = request.form
        errors = []
        role = f.get("role", "").strip()
        location = f.get("location", "").strip()
        branches = f.get("branches", "").strip()
        description = f.get("description", "").strip()
        deadline = f.get("deadline", "").strip()
        if not 2 <= len(role) <= 100:
            errors.append("Role is required (2 to 100 characters).")
        if f.get("domain") not in DOMAINS:
            errors.append("Choose a domain.")
        if not 2 <= len(location) <= 80:
            errors.append("Location is required (2 to 80 characters).")
        try:
            min_cgpa = float(f.get("min_cgpa", ""))
            if not 0 <= min_cgpa <= 10:
                raise ValueError
        except ValueError:
            errors.append("Minimum CGPA must be a number between 0 and 10.")
        try:
            stipend = int(f.get("stipend", ""))
            if stipend < 0:
                raise ValueError
        except ValueError:
            errors.append("Stipend must be a whole number (0 or more).")
        try:
            if date.fromisoformat(deadline) < date.today():
                errors.append("Deadline cannot be in the past.")
        except ValueError:
            errors.append("Enter a valid deadline date.")
        if len(branches) > 200 or len(description) > 2000:
            errors.append("Branches or description is too long.")
        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("recruiter_listings.html", listings=_mine(), domains=DOMAINS, approved=approved, form=f), 400
        cur = db.execute(
            "INSERT INTO listings (recruiter_id, role, domain, location, min_cgpa, branches, stipend, deadline, description, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (g.user["id"], role, f["domain"], location, min_cgpa, branches, stipend, deadline, description, utcnow().isoformat()),
        )
        db.commit()
        log_action(g.user["id"], "LISTING_POSTED", f"listing_id={cur.lastrowid}")
        flash("Listing posted.", "info")
        return redirect(url_for("listings.manage"))
    return render_template("recruiter_listings.html", listings=_mine(), domains=DOMAINS, approved=approved, form={})


def _mine():
    return get_db().execute(
        "SELECT l.*, (SELECT COUNT(*) FROM applications a WHERE a.listing_id = l.id) AS applicants"
        " FROM listings l WHERE recruiter_id = ? ORDER BY l.created_at DESC",
        (g.user["id"],),
    ).fetchall()
