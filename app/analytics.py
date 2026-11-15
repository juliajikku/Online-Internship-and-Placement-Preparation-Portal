"""Progress tracking and placement analytics.

Covers: FR16/FR17 (student application summary + score chart), FR18 (Admin
placement statistics with charts), FR19 (CSV report export).
"""
import csv
import io

from flask import Blueprint, Response, g, render_template

from .charts import STATUS_COLOURS, bar_chart, donut_chart, line_chart
from .db import get_db, log_action
from .security import role_required

bp = Blueprint("analytics", __name__)

ALL_STATUSES = ["Applied", "Shortlisted", "Test", "Interview", "Offered", "Accepted", "Rejected", "Closed"]


def student_dashboard_data(student_id):
    """Counts, score history and charts for the student dashboard (FR16, FR17)."""
    db = get_db()
    counts = {s: 0 for s in ALL_STATUSES}
    for r in db.execute("SELECT status, COUNT(*) AS n FROM applications WHERE student_id = ? GROUP BY status", (student_id,)):
        counts[r["status"]] = r["n"]
    attempts = db.execute(
        "SELECT score, total, submitted_at FROM attempts WHERE student_id = ? AND submitted_at IS NOT NULL ORDER BY submitted_at",
        (student_id,),
    ).fetchall()
    pct = [round(a["score"] / a["total"] * 100) for a in attempts]
    return {
        "counts": counts,
        "total_applications": sum(counts.values()),
        "placed": counts["Accepted"] > 0,
        "avg_score": round(sum(pct) / len(pct)) if pct else None,
        "attempts": len(pct),
        "status_chart": donut_chart(
            [(s, counts[s], STATUS_COLOURS[s]) for s in ALL_STATUSES if counts[s]],
            title="My applications by status",
            empty_message="No applications yet.",
        ),
        "score_chart": line_chart([a["submitted_at"][5:10] for a in attempts], pct, title="My test score trend (%)"),
    }


def _stats():
    db = get_db()

    def one(sql):
        return db.execute(sql).fetchone()[0]

    students = one("SELECT COUNT(*) FROM users WHERE role = 'student'")
    placed = one("SELECT COUNT(DISTINCT student_id) FROM applications WHERE status = 'Accepted'")
    by_status = {s: 0 for s in ALL_STATUSES}
    for r in db.execute("SELECT status, COUNT(*) AS n FROM applications GROUP BY status"):
        by_status[r["status"]] = r["n"]
    top = db.execute(
        "SELECT u.company_name AS company, COUNT(*) AS n FROM applications a"
        " JOIN listings l ON l.id = a.listing_id JOIN users u ON u.id = l.recruiter_id"
        " WHERE a.status IN ('Offered', 'Accepted') GROUP BY u.id ORDER BY n DESC, company LIMIT 6"
    ).fetchall()
    avg = db.execute(
        "SELECT AVG(CAST(score AS REAL) / total * 100) FROM attempts WHERE submitted_at IS NOT NULL AND total > 0"
    ).fetchone()[0]
    return {
        "students": students,
        "placed": placed,
        "placement_pct": round(placed / students * 100, 1) if students else 0.0,
        "recruiters": one("SELECT COUNT(*) FROM users WHERE role = 'recruiter' AND status = 'active'"),
        "listings": one("SELECT COUNT(*) FROM listings"),
        "applications": sum(by_status.values()),
        "attempts": one("SELECT COUNT(*) FROM attempts WHERE submitted_at IS NOT NULL"),
        "avg_score": round(avg) if avg is not None else None,
        "by_status": by_status,
        "top": top,
    }


@bp.route("/admin/analytics")
@role_required("admin")
def admin_analytics():
    s = _stats()
    status_chart = bar_chart(
        [(k, v) for k, v in s["by_status"].items()],
        title="Applications by status",
        empty_message="No applications yet.",
        colours=STATUS_COLOURS,
    )
    top_chart = bar_chart(
        [(r["company"] or "?", r["n"]) for r in s["top"]],
        title="Top companies by offers",
        empty_message="No offers made yet.",
    )
    return render_template("admin_analytics.html", s=s, status_chart=status_chart, top_chart=top_chart)


def _safe(cell):
    """Stop spreadsheet formula injection: cells starting with = + - @ get a leading quote."""
    text = "" if cell is None else str(cell)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


@bp.route("/admin/report.csv")
@role_required("admin")
def report_csv():
    rows = get_db().execute(
        "SELECT s.name AS student, s.email, p.branch, p.cgpa, u.company_name AS company, l.role, a.status, a.applied_at"
        " FROM applications a JOIN users s ON s.id = a.student_id JOIN listings l ON l.id = a.listing_id"
        " JOIN users u ON u.id = l.recruiter_id LEFT JOIN student_profiles p ON p.user_id = a.student_id"
        " ORDER BY a.applied_at"
    ).fetchall()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Student", "Email", "Branch", "CGPA", "Company", "Role", "Status", "Applied on"])
    for r in rows:
        writer.writerow([_safe(r[k]) for k in ("student", "email", "branch", "cgpa", "company", "role", "status")] + [r["applied_at"][:10]])
    log_action(g.user["id"], "REPORT_EXPORTED", f"rows={len(rows)}")
    return Response(
        out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=placement_report.csv"}
    )
