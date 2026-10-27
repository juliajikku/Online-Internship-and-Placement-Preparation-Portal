"""Access-control decorators and input validation helpers."""
import re
from functools import wraps

from flask import abort, g, redirect, session, url_for

from .db import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8


def load_current_user():
    """Attach the logged-in user (or None) to flask.g for this request."""
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if g.user is None:
            session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    """SE-02: only the listed roles may open the view; everyone else gets 403."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user["role"] not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def validate_registration(name, email, password, role, company_name):
    """Return a list of error messages (empty list means valid)."""
    errors = []
    if not name or not (2 <= len(name) <= 80):
        errors.append("Name must be between 2 and 80 characters.")
    if not email or len(email) > 120 or not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if not password or len(password) < MIN_PASSWORD_LEN:
        errors.append(f"Password must be at least {MIN_PASSWORD_LEN} characters.")
    if role not in ("student", "recruiter"):
        errors.append("Choose Student or Recruiter.")
    if role == "recruiter" and (not company_name or not (2 <= len(company_name) <= 100)):
        errors.append("Recruiters must enter a company name (2 to 100 characters).")
    return errors
