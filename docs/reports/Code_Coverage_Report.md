# Code Coverage Report (line coverage)

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-15
Commit: main after PR #39
Environment: Python 3.13, Flask 3, pytest 9, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=term-missing --junitxml=junit.xml`

## Summary

- Lines measured: 832
- Lines covered: 789
- **Line coverage: 94.8%**

## Per module

| Module | Line coverage | Branch coverage |
|---|---|---|
| __init__.py | 100.0% | 90.0% |
| admin.py | 100.0% | 100.0% |
| analytics.py | 100.0% | 100.0% |
| applications.py | 100.0% | 100.0% |
| aptitude.py | 85.7% | 64.7% |
| auth.py | 98.8% | 95.8% |
| charts.py | 98.7% | 95.0% |
| db.py | 100.0% | 100.0% |
| health.py | 100.0% | 100.0% |
| listings.py | 94.2% | 85.0% |
| pages.py | 88.0% | 0.0% |
| profiles.py | 92.4% | 84.2% |
| security.py | 95.3% | 88.9% |

## Lowest modules and why

- `app/aptitude.py` (86%): uncovered lines are mainly the admin test-creation validation messages and a few error paths.
- `app/pages.py` (88%): the home-page redirects for some roles.
- Every other module is 92% or higher.
