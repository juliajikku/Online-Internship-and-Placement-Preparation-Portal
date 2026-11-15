# Branch Coverage Report

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-15
Commit: main after PR #39
Environment: Python 3.13, Flask 3, pytest 9, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=term-missing --junitxml=junit.xml`

## Summary

- Branches measured: 218
- Branches covered: 187
- **Branch coverage: 85.8%**

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

## Branches not yet covered

The weakest module is `app/aptitude.py` (65% of branches): the admin form-validation error branches (bad title, bad duration, missing options) and the delete-question path. `app/pages.py` has 0% of 2 branches (role-based home redirects). These are error and redirect branches; no core use-case path is untested.

Raw data: `coverage.xml` in this folder.
