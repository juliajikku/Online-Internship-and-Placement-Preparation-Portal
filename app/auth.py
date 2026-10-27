"""Registration, login, logout.

Covers: FR1 (register/login as Student, Recruiter or Admin),
SE-01 (authenticate), SE-05 (session expiry + logout), SE-10 (bcrypt hashing),
SE-12 (lockout after repeated failed logins).
"""
from datetime import timedelta

import bcrypt
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .db import get_db, log_action, utcnow
from .security import validate_registration

bp = Blueprint("auth", __name__)

# A real bcrypt hash of a throwaway value, used so that a login for an unknown
# email takes about as long as one for a known email (avoids user enumeration).
_DUMMY_HASH = bcrypt.hashpw(b"not-a-real-password", bcrypt.gensalt())


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")
        company = request.form.get("company_name", "").strip()

        errors = validate_registration(name, email, password, role, company)
        db = get_db()
        if not errors and db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            errors.append("An account with this email already exists.")
        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("register.html", form=request.form), 400

        # Students are active immediately; recruiters wait for Admin approval (FR4).
        status = "active" if role == "student" else "pending"
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cur = db.execute(
            "INSERT INTO users (name, email, password_hash, role, status, company_name, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, hashed, role, status, company or None, utcnow().isoformat()),
        )
        db.commit()
        log_action(cur.lastrowid, "REGISTERED", f"role={role}")
        if role == "recruiter":
            flash("Registered. An Admin must approve your account before you can post listings.", "info")
        else:
            flash("Registered. You can log in now.", "info")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form={})


def _is_locked(user):
    if not user["locked_until"]:
        return False
    from datetime import datetime

    return datetime.fromisoformat(user["locked_until"]) > utcnow()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None:
            bcrypt.checkpw(password.encode("utf-8"), _DUMMY_HASH)
            flash("Invalid email or password.", "error")
            return render_template("login.html"), 401

        if _is_locked(user):
            log_action(user["id"], "LOGIN_BLOCKED_LOCKED")
            flash("Too many failed attempts. Account is locked for a short time. Try again later.", "error")
            return render_template("login.html"), 429

        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
            attempts = user["failed_attempts"] + 1
            locked_until = None
            if attempts >= current_app.config["MAX_FAILED_ATTEMPTS"]:
                locked_until = (utcnow() + timedelta(minutes=current_app.config["LOCKOUT_MINUTES"])).isoformat()
                attempts = 0
                log_action(user["id"], "ACCOUNT_LOCKED")
                # Sprint 1 deviation: the lock-notification email is only logged, not sent.
                current_app.logger.warning("Account locked, notification email would be sent to %s", user["email"])
            db.execute(
                "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
                (attempts, locked_until, user["id"]),
            )
            db.commit()
            log_action(user["id"], "LOGIN_FAILED")
            flash("Invalid email or password.", "error")
            return render_template("login.html"), 401

        if user["status"] == "rejected":
            log_action(user["id"], "LOGIN_REJECTED_ACCOUNT")
            flash("This account was not approved. Contact the placement cell.", "error")
            return render_template("login.html"), 403

        db.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?", (user["id"],))
        db.commit()
        session.clear()  # new session on login prevents session fixation
        session["user_id"] = user["id"]
        session.permanent = True  # expires after PERMANENT_SESSION_LIFETIME (SE-05)
        log_action(user["id"], "LOGIN_OK")
        return redirect(url_for("pages.dashboard"))

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
