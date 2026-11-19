# Project backlog

Every backlog item from the SRS (use cases, user stories, functional and non-functional requirements) as tracked in the GitHub Project. Story points, sprint and status are kept on the Project board. This file was updated on 19-11-2026 so that it agrees with the SRS (version 2.0) and the test reports.

Sprints: Sprint 1 = 19 to 23 Oct 2026, Sprint 2 = 26 to 30 Oct 2026.

| Issue | Item | Epic | Owner | Delivered in | Notes |
|---|---|---|---|---|---|
| #1 | Use Case1:Authenticate User | Authentication and Profile Management | Juhi | Sprint 1 |  |
| #2 | US-07:Approve recruiter accounts | Authentication and Profile Management | Julia | Sprint 1 |  |
| #3 | US-01: Filter internships by eligibility and stipend | Internship and Job listing | Juhi | Sprint 2, part 1 (PR #33) |  |
| #4 | FR1: Register/login as Student, Recruiter or Admin | Authentication and Profile Management | Juhi | Sprint 1 |  |
| #5 | FR2: Student profile creation/editing | Authentication and Profile Management | Juhi | Sprint 2, part 1 (PR #33) | Profile and resume upload (`app/profiles.py`); the issue was closed early under Sprint 1 |
| #6 | FR2: Student profile creation/editing | - | - | Closed duplicate | Duplicate of #5 (closed) |
| #7 | FR3: Recruiter company profile | Authentication and Profile Management | Julia | Sprint 1 (basic), Sprint 2 part 1 (full) | Company name captured at registration in Sprint 1; company profile page in Sprint 2 (PR #33) |
| #8 | US-05: Post internship listings with eligibility criteria | Internship and Job listing | Juhi | Sprint 2, part 1 (PR #33) |  |
| #9 | FR7: Disable Apply for ineligible students | Internship and Job listing | Juhi | Sprint 2, part 1 (PR #33) |  |
| #10 | FR8: Apply using saved profile and resume | Application lifecycle | Juhi | Sprint 2, part 1 (PR #33) |  |
| #11 | FR11: Auto-close other applications on offer acceptance | Application lifecycle | Juhi | Sprint 2, part 1 (PR #33) | Accepting an offer closes other open applications (`accept_offer`) |
| #12 | US-05: Post internship listings with eligibility criteria | Internship and Job listing | - | Closed duplicate | Duplicate of #8 (closed) |
| #13 | Use Case: Recruiter Reviews Applicants | Application lifecycle | Juhi | Sprint 2, part 1 (PR #33) |  |
| #14 | Use Case: Apply to Internship Listing | Application lifecycle | Juhi | Sprint 2, part 1 (PR #33) |  |
| #15 | US-03: Track application status | Application lifecycle | Juhi | Sprint 2, part 1 (PR #33) |  |
| #16 | US-06: View and update applicant status | Application lifecycle | Juhi | Sprint 2, part 1 (PR #33) |  |
| #17 | US-09: Manage aptitude test question bank | Aptitude Test Module | Joel | Sprint 2, part 2 (PR #34) |  |
| #18 | US-02: Take timed mock aptitude tests | Aptitude Test Module | Joel | Sprint 2, part 2 (PR #34) |  |
| #19 | Use Case: Take Aptitude Test | Aptitude Test Module | Joel | Sprint 2, part 2 (PR #34) |  |
|#20|US-08: View placement analytics|Progress Tracking and Analytics|Julia|Sprint 2, part 3 (PR #38)| Placed, placement %, top companies and a status chart. Department-wise statistics are not built (see SRS FR18 and the deviations list) |
| #21 | US-04: View test-performance trend chart | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (PR #38) |  |
| #22 | FR14: Randomize test question order | Aptitude Test Module | Joel | Sprint 2, part 2 (PR #34) |  |
| #23 | FR15: View past test scores | Progress Tracking and Analytics | Joel | Sprint 2, part 2 (PR #34) |  |
| #24 | FR16: View application history summary | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (PR #38) | Student dashboard application summary |
| #25 | FR19: Export placement report as CSV | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (PR #38) | Admin CSV report at `/admin/report.csv` |
|#26|NFR1: Page load performance|Non-Functional & Security Requirements|Julia| Sprint 2 part 3, measured in PR #37 | Page-load times measured with `scripts/load_test.py` (see docs/nfr and the System Validation Report, case ST_04). `/student` reached 3.2 s in one burst run |
|#27|NFR2: Responsive, mobile-friendly UI|Non-Functional & Security Requirements|Julia|Sprint 2, part 3 (charts and analytics)| Responsive layout in `style.css`; checked at desktop, tablet and phone sizes (ST_07) |
| #28 | NFR3: Auto-save test answers | Non-Functional & Security Requirements | Joel | Sprint 2, part 2 (PR #34) |  |
|#29|NFR4: Support 100-200 concurrent users|Non-Functional & Security Requirements|Joel| Backlog work, PR #37 (merged) | WAL mode and busy timeout in `app/db.py`; load test with 150 and 200 users, 0 failed requests (cases ST_03, ST_04, ST_06) |
|#30|NFR5: Availability during scheduled windows|Non-Functional & Security Requirements|Joel| Backlog work, PR #37 (merged) | `GET /health` returns 200, or 503 when the database fails (case ST_05). Scheduled availability windows are not built into the software |
| #31 | NFR6: Modular, maintainable codebase | Non-Functional & Security Requirements | Julia | Sprint 2, part 3 (PR #38) | Code is split into auth, admin, profiles, listings, applications, aptitude, analytics modules |
|#32|NFR7: Cross-browser/device compatibility|Non-Functional & Security Requirements|Juhi| Backlog work, PR #39 (merged) | `scripts/browser_check.py`; Chromium passes at three screen sizes. Firefox and Safari not tested (ST_07) |

## Summary
- Sprint 1 (done): 3 items (#1, #2, #4)
- Sprint 2 part 1 (merged, PR #33): 11 items
- Sprint 2 part 2 (aptitude tests, merged, PR #34): 6 items
- Sprint 2 part 3 (charts and analytics, merged, PR #38): 4 items
- Backlog work after Sprint 2 (merged): NFR4 and NFR5 (PR #37), NFR7 (PR #39)
- Closed duplicates: 2 items (#6, #12)

## SRS requirement to backlog item map
| SRS | Backlog issue(s) | Status |
|---|---|---|
| FR1 | #4 (and use case #1) | Done |
| FR2 | #5 (duplicate #6 closed) | Done |
| FR3 | #7 | Done |
| FR4 | #2 (US-07) | Done |
| FR5 | #8 (US-05, duplicate #12 closed) | Done |
| FR6 | #3 (US-01) | Done |
| FR7 | #9 | Done |
| FR8 | #10 (use case #14) | Done |
| FR9 | #15 (US-03) | Done |
| FR10 | #16 (US-06, use case #13) | Done |
| FR11 | #11 | Done |
| FR12 | #17 (US-09) | Done (Admin only, no categories) |
| FR13 | #18 (US-02, use case #19) | Done |
| FR14 | #22 | Done |
| FR15 | #23 | Done |
| FR16 | #24 | Done |
| FR17 | #21 (US-04) | Done (donut chart instead of funnel) |
| FR18 | #20 (US-08) | Partly done (no department-wise statistics) |
| FR19 | #25 | Done |
| NFR1 to NFR7 | #26, #27, #28, #29, #30, #31, #32 | Done (NFR7 on Chromium only) |

Open GitHub issues that are finished in the code and should be closed as completed: #3, #8, #9, #10, #32.
