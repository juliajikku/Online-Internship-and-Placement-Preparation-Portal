# System Validation Report

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-19
Commit: a8c52f0 on main
Environment: Python 3.13, Flask 3.1, pytest 9.1, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=xml --junitxml=junit.xml`
Case IDs (UT_, IT_, ST_, SEC_) are the Test Case IDs of the Test Plan (Test_Plan_Document.docx, section 13.1), which uses the same IDs as the SRS traceability matrix.

Scope: end-to-end user journeys across modules (IT_ cases) and non-functional requirements (ST_ cases).

## Summary

- Automated tests in this report: 17, passed 17
- Script and inspection cases: ST_04, ST_07, ST_08 (section B)

## A. Automated tests

| Test Plan case | SRS ref | pytest test | Result | Time (s) |
|---|---|---|---|---|
| IT_01 | FR9, FR10 | test_part1.py::test_recruiter_updates_status_and_student_sees_it | Pass | 0.93 |
| IT_02 | FR11 | test_part1.py::test_accepting_offer_closes_other_open_applications | Pass | 0.72 |
| IT_02 | FR11 | test_part1.py::test_cannot_accept_without_an_offer | Pass | 0.71 |
| IT_03 | FR13 | test_part2.py::test_submit_is_auto_graded | Pass | 0.71 |
| IT_04 | FR15 | test_part2.py::test_scores_page_lists_attempts_with_chart | Pass | 0.72 |
| IT_05 | FR16, FR17 | test_part3.py::test_charts_handle_empty_data | Pass | 0.00 |
| IT_05 | FR16, FR17 | test_part3.py::test_student_dashboard_shows_charts_and_counts | Pass | 0.74 |
| IT_06 | FR18 | test_part3.py::test_admin_analytics_numbers | Pass | 1.17 |
| IT_07 | FR19 | test_part3.py::test_admin_can_download_csv_report | Pass | 0.92 |
| ST_01 | FR13, NFR3 | test_part2.py::test_autosave_stores_answers | Pass | 0.75 |
| ST_02 | FR13, NFR3 | test_part2.py::test_expired_attempt_is_auto_submitted_with_saved_answers | Pass | 0.73 |
| ST_02 | FR13, NFR3 | test_part2.py::test_late_submit_only_counts_saved_answers | Pass | 0.74 |
| ST_02 | FR13, NFR3 | test_part2.py::test_restarting_resumes_the_open_attempt | Pass | 0.73 |
| ST_03 | NFR4 | test_nfr.py::test_many_students_can_log_in_and_browse_at_the_same_time | Pass | 6.81 |
| ST_05 | NFR5 | test_nfr.py::test_health_endpoint_reports_503_when_database_is_down | Pass | 0.02 |
| ST_05 | NFR5 | test_nfr.py::test_health_endpoint_reports_ok_without_login | Pass | 0.02 |
| ST_06 | NFR4 | test_nfr.py::test_database_uses_wal_mode_and_busy_timeout | Pass | 0.02 |

## B. Non-functional validation (scripts and inspection)

Load test: `scripts/load_test.py`, Flask development server, 2-core machine that also ran the load generator, measured 2026-11-05.

| Case | Requirement | Scenario | Result |
|---|---|---|---|
| ST_04 | NFR1 page load, NFR4 100-200 users | 150 users, 30 s ramp | 0 failed requests; page-view p95 0.026 s; POST /login p95 1.2 s |
| ST_04 | NFR1, NFR4 | 150 users, 5 s ramp | 0 failed; page-view p95 1.31 s; /student p95 3.2 s (slightly above the 3 s target) |
| ST_04 | NFR4 | 200 users at once | 0 failed; page-view p95 1.59 s; POST /login about 28 s (bcrypt cost 12 is deliberately slow) |
| ST_08 | NFR6 modular code | Inspection of app/ | Separate blueprint per feature: Pass |

Browser and device check: `scripts/browser_check.py`, measured 2026-11-05 (case ST_07, NFR2 and NFR7).

| Browser | Desktop 1280x800 | Tablet 768x1024 | Phone 375x667 |
|---|---|---|---|
| Chromium | Pass | Pass | Pass |
| Firefox | Not tested | Not tested | Not tested |
| WebKit (Safari engine) | Not tested | Not tested | Not tested |

Checked for every role (public, student, recruiter, admin): HTTP 200, no console errors, no sideways scrolling.

## Known limits (deviations)

- Firefox and Safari were not available in the test environment, so NFR7 is verified for Chromium only.
- Under a burst of 150-200 simultaneous logins, login takes many seconds because of bcrypt; normal page views stay fast.
- The confirmation e-mail on apply is only written to the log, because the demo has no mail server.
- The load-test and browser-check results are from 2026-11-05; the pytest results are from 2026-11-19.
