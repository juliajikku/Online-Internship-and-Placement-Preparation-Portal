# Unit Test Report

Project: Online Internship & Placement Preparation Portal
Run date: 2026-11-19
Commit: a8c52f0 on main
Environment: Python 3.13, Flask 3.1, pytest 9.1, pytest-cov, SQLite (Linux)
Command: `pytest --cov=app --cov-branch --cov-report=xml --junitxml=junit.xml`
Case IDs (UT_, IT_, ST_, SEC_) are the Test Case IDs of the Test Plan (Test_Plan_Document.docx, section 13.1), which uses the same IDs as the SRS traceability matrix.

Scope: single-rule tests (validation, permissions, stored data, security). Multi-step flows and non-functional checks are in the System Validation Report.

## Summary

- Automated tests in this report: 66
- Passed: 66
- Failed: 0
- Whole suite (this report + System Validation Report): 83 of 83 passed

## Results

| Test Plan case | SRS ref | pytest test | Result | Time (s) |
|---|---|---|---|---|
| UT_01 | FR1 | test_auth.py::test_student_can_register_and_is_active | Pass | 0.26 |
| UT_02 | FR1 | test_auth.py::test_duplicate_email_rejected | Pass | 0.26 |
| UT_02 | FR1 | test_auth.py::test_weak_password_and_bad_email_rejected | Pass | 0.03 |
| UT_03 | FR1, SR | test_auth.py::test_password_is_stored_hashed | Pass | 0.26 |
| UT_04 | FR1 | test_auth.py::test_each_role_lands_on_its_own_dashboard | Pass | 0.48 |
| UT_04 | FR1 | test_auth.py::test_student_login_redirects_to_student_dashboard | Pass | 0.48 |
| UT_05 | FR2 | test_part1.py::test_student_saves_profile_with_valid_pdf | Pass | 0.49 |
| UT_06 | FR2 | test_part1.py::test_saved_profile_page_reopens_with_values | Pass | 0.50 |
| UT_07 | FR2 | test_part1.py::test_resume_with_wrong_type_is_rejected | Pass | 0.48 |
| UT_08 | FR2 | test_part1.py::test_resume_over_5mb_is_rejected | Pass | 0.50 |
| UT_09 | FR2 | test_part1.py::test_fake_pdf_content_is_rejected | Pass | 0.49 |
| UT_10 | FR2 | test_part1.py::test_invalid_cgpa_rejected | Pass | 0.49 |
| UT_11 | FR3 | test_part1.py::test_company_website_must_be_http | Pass | 0.48 |
| UT_11 | FR3 | test_auth.py::test_recruiter_requires_company_name | Pass | 0.03 |
| UT_11 | FR3 | test_part1.py::test_recruiter_updates_company_profile | Pass | 0.48 |
| UT_12 | FR4 | test_admin.py::test_admin_can_approve_recruiter | Pass | 0.71 |
| UT_12 | FR4 | test_admin.py::test_admin_sees_pending_recruiters | Pass | 0.73 |
| UT_12 | FR4 | test_admin.py::test_approved_recruiter_sees_approved_badge | Pass | 0.95 |
| UT_12 | FR4 | test_auth.py::test_recruiter_registers_as_pending | Pass | 0.26 |
| UT_13 | FR4 | test_admin.py::test_admin_can_reject_recruiter | Pass | 0.70 |
| UT_13 | FR4 | test_admin.py::test_already_reviewed_recruiter_cannot_be_changed | Pass | 0.70 |
| UT_13 | FR4 | test_auth.py::test_rejected_recruiter_cannot_log_in | Pass | 0.49 |
| UT_13 | FR4 | test_admin.py::test_unknown_recruiter_id_returns_404 | Pass | 0.53 |
| UT_14 | FR5 | test_part1.py::test_approved_recruiter_can_post_listing | Pass | 0.50 |
| UT_15 | FR5 | test_part1.py::test_pending_recruiter_cannot_post_listing | Pass | 0.50 |
| UT_15 | FR5 | test_admin.py::test_pending_recruiter_sees_awaiting_approval_message | Pass | 0.48 |
| UT_16 | FR5 | test_part1.py::test_listing_deadline_in_past_rejected | Pass | 0.50 |
| UT_16 | FR5 | test_part1.py::test_listing_requires_all_criteria | Pass | 0.51 |
| UT_17 | FR6 | test_part1.py::test_students_only_see_active_unexpired_listings | Pass | 0.93 |
| UT_18 | FR6 | test_part1.py::test_filters_can_be_combined | Pass | 0.71 |
| UT_19 | FR7 | test_part1.py::test_ineligible_cgpa_is_blocked_and_reason_shown | Pass | 0.72 |
| UT_20 | FR7 | test_part1.py::test_wrong_branch_is_blocked | Pass | 0.69 |
| UT_21 | FR8 | test_part1.py::test_eligible_student_can_apply | Pass | 0.72 |
| UT_22 | FR8 | test_part1.py::test_cannot_apply_to_expired_listing | Pass | 0.69 |
| UT_22 | FR8 | test_part1.py::test_cannot_apply_twice | Pass | 0.70 |
| UT_22 | FR8 | test_part1.py::test_cannot_apply_without_resume | Pass | 0.69 |
| UT_23 | FR9 | test_part1.py::test_final_statuses_cannot_be_changed | Pass | 0.71 |
| UT_23 | FR9 | test_part1.py::test_invalid_status_value_rejected | Pass | 0.70 |
| UT_23 | FR9 | test_part1.py::test_student_cannot_update_status | Pass | 0.71 |
| UT_24 | FR10 | test_part1.py::test_recruiter_cannot_see_other_recruiters_applicants | Pass | 0.92 |
| UT_25 | FR12 | test_part2.py::test_admin_creates_test_and_questions | Pass | 0.50 |
| UT_25 | FR12 | test_part2.py::test_question_needs_all_options | Pass | 0.48 |
| UT_26 | FR14 | test_part2.py::test_question_order_is_a_random_permutation | Pass | 0.80 |
| SEC_01 | SR (login) | test_auth.py::test_account_locks_after_five_failed_attempts | Pass | 1.40 |
| SEC_01 | SR (login) | test_auth.py::test_lock_expires_after_lockout_period | Pass | 1.61 |
| SEC_02 | SR (login) | test_auth.py::test_unknown_email_gives_same_generic_error | Pass | 0.25 |
| SEC_02 | SR (login) | test_auth.py::test_wrong_password_gives_generic_error | Pass | 0.48 |
| SEC_03 | SR (CSRF) | test_auth.py::test_form_post_without_csrf_token_is_rejected | Pass | 0.02 |
| SEC_04 | SR (access) | test_auth.py::test_cannot_self_register_as_admin | Pass | 0.03 |
| SEC_04 | SR (access) | test_auth.py::test_login_is_required_for_dashboards | Pass | 0.02 |
| SEC_04 | SR (access) | test_admin.py::test_recruiter_cannot_approve_themselves | Pass | 0.48 |
| SEC_04 | SR (access) | test_part2.py::test_student_cannot_manage_tests | Pass | 0.49 |
| SEC_04 | SR (access) | test_part3.py::test_student_cannot_open_admin_analytics_or_report | Pass | 0.47 |
| SEC_04 | SR (access) | test_admin.py::test_student_cannot_open_admin_page_or_approve | Pass | 0.71 |
| SEC_04 | SR (access) | test_part1.py::test_student_cannot_post_listing | Pass | 0.49 |
| SEC_05 | SR (data) | test_part1.py::test_cannot_accept_someone_elses_offer | Pass | 0.93 |
| SEC_05 | SR (data) | test_part1.py::test_recruiter_cannot_open_student_profile | Pass | 0.50 |
| SEC_05 | SR (data) | test_part1.py::test_resume_access_rules | Pass | 1.86 |
| SEC_05 | SR (data) | test_part2.py::test_student_cannot_open_another_students_attempt | Pass | 1.21 |
| SEC_06 | SR (test integrity) | test_part2.py::test_correct_answers_are_never_sent_before_submission | Pass | 0.73 |
| SEC_07 | SR (injection) | test_part3.py::test_chart_labels_are_escaped | Pass | 0.00 |
| SEC_07 | SR (injection) | test_part3.py::test_csv_neutralises_formula_injection | Pass | 0.95 |
| SEC_08 | SR (audit) | test_part1.py::test_application_is_written_to_audit_log | Pass | 0.70 |
| SEC_08 | SR (audit) | test_admin.py::test_approval_is_written_to_audit_log | Pass | 0.70 |
| SEC_08 | SR (audit) | test_auth.py::test_failed_login_is_written_to_audit_log | Pass | 0.47 |
| SEC_09 | SR (session) | test_auth.py::test_logout_ends_session | Pass | 0.48 |

## Notes

- Every test uses a fresh temporary SQLite database, so tests do not depend on each other.
- One Test Plan case can be verified by several pytest functions; a test is listed under the first case it supports.
- Defect found during testing: DEF_01 (student profile page error after saving), fixed in Sprint 2 and covered by UT_06.
