# Code Coverage Report (line coverage)

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-19
Commit: a8c52f0 on main
Environment: Python 3.13, Flask 3.1, pytest 9.1, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=xml --junitxml=junit.xml`
Case IDs (UT_, IT_, ST_, SEC_) are the Test Case IDs of the Test Plan (Test_Plan_Document.docx, section 13.1), which uses the same IDs as the SRS traceability matrix.

## Summary

- Lines measured: 832
- Lines covered: 789
- **Line coverage: 94.8%**
- Tests run: 83, passed 83

## Per module

| Module | Lines | Lines covered | Line coverage | Missed lines |
|---|---|---|---|---|
| __init__.py | 46 | 46 | 100.0% | none |
| admin.py | 33 | 33 | 100.0% | none |
| analytics.py | 49 | 49 | 100.0% | none |
| applications.py | 80 | 80 | 100.0% | none |
| aptitude.py | 154 | 132 | 85.7% | 32-34, 36, 45, 48, 57, 80-86, 93, 96, 105, 108-109, 165, 184, 209 |
| auth.py | 83 | 82 | 98.8% | 56 |
| charts.py | 76 | 75 | 98.7% | 96 |
| db.py | 25 | 25 | 100.0% | none |
| health.py | 10 | 10 | 100.0% | none |
| listings.py | 103 | 97 | 94.2% | 96, 98, 102, 108, 117, 131 |
| pages.py | 25 | 22 | 88.0% | 13-15 |
| profiles.py | 105 | 97 | 92.4% | 25, 63, 65, 106, 108, 126-127, 149 |
| security.py | 43 | 41 | 95.3% | 20, 53 |

## Lowest modules

- aptitude.py: 85.7%
- pages.py: 88.0%
- profiles.py: 92.4%

The missed lines are mainly error and validation paths (for example admin form-validation messages in aptitude.py). No core use-case path is untested.

Raw data: coverage.xml in this folder (the full list of lines).
