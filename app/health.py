"""Health check used to confirm the portal is available (NFR5).

GET /health answers 200 with {"status": "ok"} when the app can reach its database,
and 503 otherwise. An uptime monitor (or the deployment platform) can poll it
before and during scheduled application and test windows.
"""
from flask import Blueprint, jsonify

from .db import get_db, utcnow

bp = Blueprint("health", __name__)


@bp.route("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
    except Exception:  # any database failure means the portal cannot serve users
        return jsonify(status="unavailable", database="error"), 503
    return jsonify(status="ok", database="ok", time=utcnow().isoformat())
