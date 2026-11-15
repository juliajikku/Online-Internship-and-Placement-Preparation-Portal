# System Validation Report

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-15
Commit: main after PR #39
Environment: Python 3.13, Flask 3, pytest 9, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=term-missing --junitxml=junit.xml`

These tests follow a whole user journey across several modules, or check a non-functional requirement.

## Summary

- Automated system tests: 14, passed 14

## A. Automated end-to-end tests

| ID | Test file | Test case | Covers | Result | Time (s) |
|---|---|---|---|---|---|
| SV_01 | test_admin.py | admin can approve recruiter | FR4 (admin approval) | Pass | 1.03 |
| SV_02 | test_auth.py | each role lands on its own dashboard | FR1 (register/login), security | Pass | 0.67 |
| SV_03 | test_nfr.py | many students can log in and browse at the same time | NFR4, NFR5 | Pass | 9.79 |
| SV_04 | test_part1.py | approved recruiter can post listing | FR2, FR3, FR5-FR11 | Pass | 0.72 |
| SV_05 | test_part1.py | students only see active unexpired listings | FR2, FR3, FR5-FR11 | Pass | 1.37 |
| SV_06 | test_part1.py | eligible student can apply | FR2, FR3, FR5-FR11 | Pass | 1.03 |
| SV_07 | test_part1.py | recruiter updates status and student sees it | FR2, FR3, FR5-FR11 | Pass | 1.36 |
| SV_08 | test_part1.py | accepting offer closes other open applications | FR2, FR3, FR5-FR11 | Pass | 1.01 |
| SV_09 | test_part2.py | correct answers are never sent before submission | FR12-FR15, NFR3 | Pass | 1.01 |
| SV_10 | test_part2.py | submit is auto graded | FR12-FR15, NFR3 | Pass | 1.01 |
| SV_11 | test_part2.py | expired attempt is auto submitted with saved answers | FR12-FR15, NFR3 | Pass | 1.01 |
| SV_12 | test_part3.py | student dashboard shows charts and counts | FR16-FR19 | Pass | 1.02 |
| SV_13 | test_part3.py | admin analytics numbers | FR16-FR19 | Pass | 1.72 |
| SV_14 | test_part3.py | admin can download csv report | FR16-FR19 | Pass | 1.30 |

## B. Non-functional validation (measured)

Load test: `scripts/load_test.py`, Flask development server, 2-core machine that also ran the load generator, measured 2026-11-05.

| Requirement | Scenario | Result |
|---|---|---|
| NFR1 page load 2-3 s | 150 users, 30 s ramp | 0 failed requests; page-view p95 0.026 s |
| NFR1 page load 2-3 s | 150 users, 5 s ramp | 0 failed; page-view p95 1.31 s; /student p95 3.2 s (slightly above the 3 s target) |
| NFR4 100-200 users | 200 users at once | 0 failed; page-view p95 1.59 s; POST /login about 28 s (bcrypt cost 12 is deliberately slow) |
| NFR5 availability | `/health` endpoint | Returns 200 when the database works and 503 when it does not (automated test) |
| NFR3 auto-save | autosave and expired-attempt tests | Pass |

Browser and device check: `scripts/browser_check.py`, measured 2026-11-05.

| Browser | Desktop 1280x800 | Tablet 768x1024 | Phone 375x667 |
|---|---|---|---|
| Chromium | Pass | Pass | Pass |
| Firefox | Not tested | Not tested | Not tested |
| WebKit (Safari engine) | Not tested | Not tested | Not tested |

Checked for every role (public, student, recruiter, admin): HTTP 200, no console errors, no sideways scrolling.

## Known limits (deviations)

- Firefox and Safari were not available in the test environment, so NFR7 is verified for Chromium only.
- Under a burst of 150-200 simultaneous logins, login takes many seconds because of bcrypt; normal page views stay fast.
- The confirmation email on apply is only written to the log, because the demo has no mail server.
