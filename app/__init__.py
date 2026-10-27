"""Online Internship & Placement Preparation Portal - Sprint 1 application factory."""
import os
import secrets
from datetime import timedelta

from flask import Flask, abort, render_template, request, session

from . import admin, auth, db, pages
from .security import load_current_user


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Set SECRET_KEY in the environment for a stable key; otherwise a random
        # key is generated per run (sessions then reset when the app restarts).
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.path.join(app.instance_path, "portal.db"),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # Set COOKIE_SECURE=1 when serving over HTTPS (SE-04).
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
        MAX_FAILED_ATTEMPTS=5,
        LOCKOUT_MINUTES=15,
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    with app.app_context():
        db.init_db()

    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(pages.bp)

    @app.before_request
    def _before():
        load_current_user()
        if request.method == "POST":  # CSRF protection for every form post
            token = session.get("csrf")
            sent = request.form.get("csrf_token", "")
            if not token or not secrets.compare_digest(token, sent):
                abort(400)

    @app.context_processor
    def _inject_csrf():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return {"csrf_token": session["csrf"]}

    @app.after_request
    def _security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Content-Security-Policy"] = "default-src 'self'"
        return resp

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    def _error(err):
        messages = {400: "Bad request or expired form.", 403: "You do not have access to this page.", 404: "Page not found."}
        return render_template("error.html", code=err.code, message=messages[err.code]), err.code

    return app
