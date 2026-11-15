# Unit Test Report

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-15
Commit: main after PR #39
Environment: Python 3.13, Flask 3, pytest 9, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=term-missing --junitxml=junit.xml`

How tests are grouped: the tests call one route or one module and check one rule (validation, permission, status code, stored data). Multi-step flows are in the System Validation Report.

## Summary

- Tests in this report: 69
- Passed: 69
- Failed: 0
- Whole suite (unit + system): 83/83 passed

## Results

| ID | Test file | Test case | Covers | Result | Time (s) |
|---|---|---|---|---|---|
| UT_01 | test_admin.py | admin sees pending recruiters | FR4 (admin approval) | Pass | 1.05 |
| UT_02 | test_admin.py | admin can reject recruiter | FR4 (admin approval) | Pass | 0.99 |
| UT_03 | test_admin.py | approval is written to audit log | FR4 (admin approval) | Pass | 1.05 |
| UT_04 | test_admin.py | already reviewed recruiter cannot be changed | FR4 (admin approval) | Pass | 1.05 |
| UT_05 | test_admin.py | student cannot open admin page or approve | FR4 (admin approval) | Pass | 1.03 |
| UT_06 | test_admin.py | recruiter cannot approve themselves | FR4 (admin approval) | Pass | 0.68 |
| UT_07 | test_admin.py | pending recruiter sees awaiting approval message | FR4 (admin approval) | Pass | 0.70 |
| UT_08 | test_admin.py | approved recruiter sees approved badge | FR4 (admin approval) | Pass | 1.31 |
| UT_09 | test_admin.py | unknown recruiter id returns 404 | FR4 (admin approval) | Pass | 0.66 |
| UT_10 | test_auth.py | student can register and is active | FR1 (register/login), security | Pass | 0.34 |
| UT_11 | test_auth.py | recruiter registers as pending | FR1 (register/login), security | Pass | 0.34 |
| UT_12 | test_auth.py | recruiter requires company name | FR1 (register/login), security | Pass | 0.04 |
| UT_13 | test_auth.py | cannot self register as admin | FR1 (register/login), security | Pass | 0.04 |
| UT_14 | test_auth.py | weak password and bad email rejected | FR1 (register/login), security | Pass | 0.04 |
| UT_15 | test_auth.py | duplicate email rejected | FR1 (register/login), security | Pass | 0.37 |
| UT_16 | test_auth.py | password is stored hashed | FR1 (register/login), security | Pass | 0.39 |
| UT_17 | test_auth.py | student login redirects to student dashboard | FR1 (register/login), security | Pass | 0.69 |
| UT_18 | test_auth.py | wrong password gives generic error | FR1 (register/login), security | Pass | 0.68 |
| UT_19 | test_auth.py | unknown email gives same generic error | FR1 (register/login), security | Pass | 0.37 |
| UT_20 | test_auth.py | rejected recruiter cannot log in | FR1 (register/login), security | Pass | 0.72 |
| UT_21 | test_auth.py | account locks after five failed attempts | FR1 (register/login), security | Pass | 1.98 |
| UT_22 | test_auth.py | lock expires after lockout period | FR1 (register/login), security | Pass | 2.28 |
| UT_23 | test_auth.py | logout ends session | FR1 (register/login), security | Pass | 0.68 |
| UT_24 | test_auth.py | login is required for dashboards | FR1 (register/login), security | Pass | 0.03 |
| UT_25 | test_auth.py | form post without csrf token is rejected | FR1 (register/login), security | Pass | 0.04 |
| UT_26 | test_auth.py | failed login is written to audit log | FR1 (register/login), security | Pass | 0.69 |
| UT_27 | test_nfr.py | health endpoint reports ok without login | NFR4, NFR5 | Pass | 0.02 |
| UT_28 | test_nfr.py | health endpoint reports 503 when database is down | NFR4, NFR5 | Pass | 0.04 |
| UT_29 | test_nfr.py | database uses wal mode and busy timeout | NFR4, NFR5 | Pass | 0.04 |
| UT_30 | test_part1.py | student saves profile with valid pdf | FR2, FR3, FR5-FR11 | Pass | 0.72 |
| UT_31 | test_part1.py | saved profile page reopens with values | FR2, FR3, FR5-FR11 | Pass | 0.74 |
| UT_32 | test_part1.py | resume with wrong type is rejected | FR2, FR3, FR5-FR11 | Pass | 0.69 |
| UT_33 | test_part1.py | resume over 5mb is rejected | FR2, FR3, FR5-FR11 | Pass | 0.70 |
| UT_34 | test_part1.py | fake pdf content is rejected | FR2, FR3, FR5-FR11 | Pass | 0.67 |
| UT_35 | test_part1.py | invalid cgpa rejected | FR2, FR3, FR5-FR11 | Pass | 0.70 |
| UT_36 | test_part1.py | recruiter cannot open student profile | FR2, FR3, FR5-FR11 | Pass | 0.70 |
| UT_37 | test_part1.py | recruiter updates company profile | FR2, FR3, FR5-FR11 | Pass | 0.69 |
| UT_38 | test_part1.py | company website must be http | FR2, FR3, FR5-FR11 | Pass | 0.71 |
| UT_39 | test_part1.py | pending recruiter cannot post listing | FR2, FR3, FR5-FR11 | Pass | 0.69 |
| UT_40 | test_part1.py | listing requires all criteria | FR2, FR3, FR5-FR11 | Pass | 0.70 |
| UT_41 | test_part1.py | listing deadline in past rejected | FR2, FR3, FR5-FR11 | Pass | 0.67 |
| UT_42 | test_part1.py | student cannot post listing | FR2, FR3, FR5-FR11 | Pass | 0.69 |
| UT_43 | test_part1.py | filters can be combined | FR2, FR3, FR5-FR11 | Pass | 1.07 |
| UT_44 | test_part1.py | ineligible cgpa is blocked and reason shown | FR2, FR3, FR5-FR11 | Pass | 1.05 |
| UT_45 | test_part1.py | wrong branch is blocked | FR2, FR3, FR5-FR11 | Pass | 1.01 |
| UT_46 | test_part1.py | cannot apply without resume | FR2, FR3, FR5-FR11 | Pass | 1.02 |
| UT_47 | test_part1.py | cannot apply twice | FR2, FR3, FR5-FR11 | Pass | 0.99 |
| UT_48 | test_part1.py | cannot apply to expired listing | FR2, FR3, FR5-FR11 | Pass | 0.98 |
| UT_49 | test_part1.py | application is written to audit log | FR2, FR3, FR5-FR11 | Pass | 1.02 |
| UT_50 | test_part1.py | recruiter cannot see other recruiters applicants | FR2, FR3, FR5-FR11 | Pass | 1.36 |
| UT_51 | test_part1.py | invalid status value rejected | FR2, FR3, FR5-FR11 | Pass | 0.99 |
| UT_52 | test_part1.py | final statuses cannot be changed | FR2, FR3, FR5-FR11 | Pass | 0.98 |
| UT_53 | test_part1.py | student cannot update status | FR2, FR3, FR5-FR11 | Pass | 0.98 |
| UT_54 | test_part1.py | cannot accept without an offer | FR2, FR3, FR5-FR11 | Pass | 1.01 |
| UT_55 | test_part1.py | cannot accept someone elses offer | FR2, FR3, FR5-FR11 | Pass | 1.33 |
| UT_56 | test_part1.py | resume access rules | FR2, FR3, FR5-FR11 | Pass | 2.66 |
| UT_57 | test_part2.py | admin creates and questions | FR12-FR15, NFR3 | Pass | 0.72 |
| UT_58 | test_part2.py | question needs all options | FR12-FR15, NFR3 | Pass | 0.66 |
| UT_59 | test_part2.py | student cannot manage tests | FR12-FR15, NFR3 | Pass | 0.70 |
| UT_60 | test_part2.py | question order is a random permutation | FR12-FR15, NFR3 | Pass | 1.05 |
| UT_61 | test_part2.py | autosave stores answers | FR12-FR15, NFR3 | Pass | 1.00 |
| UT_62 | test_part2.py | late submit only counts saved answers | FR12-FR15, NFR3 | Pass | 1.00 |
| UT_63 | test_part2.py | student cannot open another students attempt | FR12-FR15, NFR3 | Pass | 1.68 |
| UT_64 | test_part2.py | restarting resumes the open attempt | FR12-FR15, NFR3 | Pass | 1.02 |
| UT_65 | test_part2.py | scores page lists attempts with chart | FR12-FR15, NFR3 | Pass | 1.00 |
| UT_66 | test_part3.py | student cannot open admin analytics or report | FR16-FR19 | Pass | 0.68 |
| UT_67 | test_part3.py | csv neutralises formula injection | FR16-FR19 | Pass | 1.30 |
| UT_68 | test_part3.py | charts handle empty data | FR16-FR19 | Pass | 0.00 |
| UT_69 | test_part3.py | chart labels are escaped | FR16-FR19 | Pass | 0.00 |

## Notes

- Every test uses a fresh temporary SQLite database, so tests do not depend on each other.
- Unit tests were updated during Sprint 2 to match the final behaviour, for example the resume rules (PDF/DOCX, 5 MB, real file content) and the Apply button being blocked for ineligible students.
