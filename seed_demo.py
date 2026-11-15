"""Optional: load demo data so the product can be shown without typing it all in.

Creates an approved demo recruiter with three listings and one 10-question
aptitude test. Run after seed_admin.py:   python seed_demo.py
Demo recruiter login: recruiter@demo.com / Demo@12345  (demo only, change or delete for real use)
"""
import sys
from datetime import date, timedelta

import bcrypt

from app import create_app
from app.db import get_db, utcnow

QUESTIONS = [
    ("What is 15% of 240?", "30", "36", "40", "24", "b"),
    ("A train travels 120 km in 2 hours. What is its speed?", "50 km/h", "60 km/h", "70 km/h", "80 km/h", "b"),
    ("Find the next number: 2, 6, 12, 20, ?", "28", "30", "32", "26", "b"),
    ("If 3x + 5 = 20, what is x?", "3", "4", "5", "6", "c"),
    ("The average of 10, 20 and 30 is:", "15", "20", "25", "30", "b"),
    ("Which word is the odd one out?", "Apple", "Mango", "Carrot", "Banana", "c"),
    ("A shop gives 20% off a Rs 500 item. The price is:", "Rs 380", "Rs 400", "Rs 420", "Rs 450", "b"),
    ("Simple interest on Rs 1000 at 10% for 2 years is:", "Rs 100", "Rs 150", "Rs 200", "Rs 250", "c"),
    ("If A is taller than B and B is taller than C, who is shortest?", "A", "B", "C", "Cannot say", "c"),
    ("How many minutes are there in 2.5 hours?", "120", "150", "180", "200", "b"),
]


def main():
    app = create_app()
    with app.app_context():
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE email = 'recruiter@demo.com'").fetchone():
            print("Demo data already exists. Nothing changed.")
            return 1
        now = utcnow().isoformat()
        h = bcrypt.hashpw(b"Demo@12345", bcrypt.gensalt())
        rid = db.execute(
            "INSERT INTO users (name, email, password_hash, role, status, company_name, created_at)"
            " VALUES ('Demo Recruiter', 'recruiter@demo.com', ?, 'recruiter', 'active', 'TechNova Pvt Ltd', ?)",
            (h, now),
        ).lastrowid
        deadline = (date.today() + timedelta(days=45)).isoformat()
        for role, domain, loc, cg, br, st in [
            ("Software Engineering Intern", "Software", "Bengaluru", 7.0, "CSE, ISE", 25000),
            ("Data Analyst Intern", "Data Science", "Remote", 7.5, "", 20000),
            ("Embedded Systems Intern", "Electronics", "Pune", 6.5, "ECE, EEE", 18000),
        ]:
            db.execute(
                "INSERT INTO listings (recruiter_id, role, domain, location, min_cgpa, branches, stipend, deadline, description, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Demo listing for the Sprint 2 walkthrough.', ?)",
                (rid, role, domain, loc, cg, br, st, deadline, now),
            )
        admin = db.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
        tid = db.execute(
            "INSERT INTO tests (title, duration_minutes, created_by, created_at) VALUES ('Quantitative Aptitude 1', 10, ?, ?)",
            (admin["id"] if admin else rid, now),
        ).lastrowid
        for q in QUESTIONS:
            db.execute(
                "INSERT INTO questions (test_id, text, option_a, option_b, option_c, option_d, correct) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tid, *q),
            )
        db.commit()
    print("Demo data created: recruiter@demo.com / Demo@12345, 3 listings, 1 test with 10 questions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
