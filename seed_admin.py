"""Create the first Admin account (Admins cannot self-register).

Usage:
    python seed_admin.py                      # random password, printed once
    ADMIN_EMAIL=tpo@college.edu ADMIN_PASSWORD='choose-a-strong-one' python seed_admin.py
"""
import os
import secrets
import sys

import bcrypt

from app import create_app
from app.db import get_db, log_action, utcnow


def main():
    email = os.environ.get("ADMIN_EMAIL", "admin@portal.local").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(12)
    generated = "ADMIN_PASSWORD" not in os.environ or not os.environ["ADMIN_PASSWORD"]

    app = create_app()
    with app.app_context():
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            print(f"An account for {email} already exists. Nothing changed.")
            return 1
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cur = db.execute(
            "INSERT INTO users (name, email, password_hash, role, status, created_at)"
            " VALUES (?, ?, ?, 'admin', 'active', ?)",
            ("Placement Cell Admin", email, hashed, utcnow().isoformat()),
        )
        db.commit()
        log_action(cur.lastrowid, "ADMIN_SEEDED")

    print(f"Admin created: {email}")
    if generated:
        print(f"Generated password (shown once, save it now): {password}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
