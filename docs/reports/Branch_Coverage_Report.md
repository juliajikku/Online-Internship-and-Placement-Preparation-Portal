# Branch Coverage Report

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-19
Commit: a8c52f0 on main
Environment: Python 3.13, Flask 3.1, pytest 9.1, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=xml --junitxml=junit.xml`
Case IDs (UT_, IT_, ST_, SEC_) are the Test Case IDs of the Test Plan (Test_Plan_Document.docx, section 13.1), which uses the same IDs as the SRS traceability matrix.

## Summary

- Branches measured: 218
- Branches covered: 187
- **Branch coverage: 85.8%**
- Tests run: 83, passed 83

## Per module

| Module | Branches | Branches covered | Branch coverage |
|---|---|---|---|
| __init__.py | 10 | 9 | 90.0% |
| admin.py | 4 | 4 | 100.0% |
| analytics.py | 6 | 6 | 100.0% |
| applications.py | 18 | 18 | 100.0% |
| aptitude.py | 34 | 22 | 64.7% |
| auth.py | 24 | 23 | 95.8% |
| charts.py | 20 | 19 | 95.0% |
| db.py | 4 | 4 | 100.0% |
| health.py | 0 | 0 | 100.0% (no branches) |
| listings.py | 40 | 34 | 85.0% |
| pages.py | 2 | 0 | 0.0% |
| profiles.py | 38 | 32 | 84.2% |
| security.py | 18 | 16 | 88.9% |

## Lowest modules

- pages.py: 0.0%
- aptitude.py: 64.7%
- profiles.py: 84.2%

pages.py shows 0% because both of its 2 branches are in one place: the `/` home route when a user is already logged in (redirect to the dashboard) is not tested directly; the dashboard itself is tested. The other uncovered branches are mainly error and validation outcomes (for example invalid admin test or question forms in aptitude.py, and some resume-upload error paths in profiles.py).

Raw data: coverage.xml in this folder.
