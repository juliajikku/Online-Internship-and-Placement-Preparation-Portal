# Project backlog

Every backlog item from the SRS (use cases, user stories, functional and non-functional requirements) as tracked in the GitHub Project. Story points, sprint and status are kept on the Project board.

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
| #17 | US-09: Manage aptitude test question bank | Aptitude Test Module | Joel | Sprint 2, part 2 (aptitude tests) |  |
| #18 | US-02: Take timed mock aptitude tests | Aptitude Test Module | Joel | Sprint 2, part 2 (aptitude tests) |  |
| #19 | Use Case: Take Aptitude Test | Aptitude Test Module | Joel | Sprint 2, part 2 (aptitude tests) |  |
| #20 | US-08: View placement analytics | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (charts and analytics) |  |
| #21 | US-04: View test-performance trend chart | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (charts and analytics) |  |
| #22 | FR14: Randomize test question order | Aptitude Test Module | Joel | Sprint 2, part 2 (aptitude tests) |  |
| #23 | FR15: View past test scores | Progress Tracking and Analytics | Joel | Sprint 2, part 2 (aptitude tests) |  |
| #24 | FR16: View application history summary | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (charts and analytics) | Student dashboard application summary |
| #25 | FR19: Export placement report as CSV | Progress Tracking and Analytics | Julia | Sprint 2, part 3 (charts and analytics) | Admin CSV report at `/admin/report.csv` |
| #26 | NFR1: Page load performance | Non-Functional & Security Requirements | Julia | Sprint 2, part 3 (charts and analytics) |  |
| #27 | NFR2: Responsive, mobile-friendly UI | Non-Functional & Security Requirements | Julia | Sprint 2, part 3 (charts and analytics) | Responsive layout in `style.css` |
| #28 | NFR3: Auto-save test answers | Non-Functional & Security Requirements | Joel | Sprint 2, part 2 (aptitude tests) |  |
| #29 | NFR4: Support 100-200 concurrent users | Non-Functional & Security Requirements | Joel | Backlog (not built) | Not built. Planned load test for 100 to 200 users |
| #30 | NFR5: Availability during scheduled windows | Non-Functional & Security Requirements | Joel | Backlog (not built) | Not built. Planned availability windows |
| #31 | NFR6: Modular, maintainable codebase | Non-Functional & Security Requirements | Julia | Sprint 2, part 3 (charts and analytics) | Code is split into auth, admin, profiles, listings, applications, aptitude, analytics modules |
| #32 | NFR7: Cross-browser/device compatibility | Non-Functional & Security Requirements | Juhi | Backlog (not built) | Not built. Planned Chrome and Firefox cross-browser testing |

## Summary
- Sprint 1 (done): 3 items (#1, #2, #4)
- Sprint 2 part 1 (merged, PR #33): 11 items
- Sprint 2 part 2 (aptitude tests): 6 items
- Sprint 2 part 3 (charts and analytics): 7 items
- Backlog, not built: 3 items (NFR4 load capacity, NFR5 availability windows, NFR7 cross-browser testing)
- Closed duplicates: 2 items (#6, #12)
