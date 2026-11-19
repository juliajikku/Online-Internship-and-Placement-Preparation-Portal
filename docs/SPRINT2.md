# Sprint 2 notes

## What was built
| Use case / story | What it does |
|---|---|
| Use Case: Apply to Internship Listing | Student browses and filters listings, sees why Apply is disabled when ineligible, applies with the saved profile and resume |
| Use Case: Recruiter Reviews Applicants | Recruiter sees applicants for their own listings (CGPA, branch, best test score, resume) and updates the status |
| Use Case: Take Aptitude Test | Timed test, randomised question order, auto-save every 30 s, auto-submit when time ends, auto-graded score |
| US-04 test-performance chart, US-08 placement analytics, US-09 question bank | Student score trend and status charts, Admin analytics charts with CSV export, Admin creates tests and questions |

## Requirements covered
| Requirement | Where |
|---|---|
| FR2 student profile and resume upload | `app/profiles.py`, `student_profile.html` |
| FR3 recruiter company profile | `app/profiles.py`, `recruiter_profile.html` |
| FR5 post listings with eligibility criteria | `app/listings.py` (`manage`) |
| FR6 search and filter listings | `app/listings.py` (`browse`): text, domain, location, minimum stipend; expired listings hidden |
| FR7 disable Apply for ineligible students | `eligibility()` in `app/listings.py`; button disabled in the page and re-checked on the server |
| FR8 apply with saved profile and resume | `app/applications.py` (`apply`), one application per listing |
| FR9 / FR10 status tracking and recruiter updates | Applied, Shortlisted, Test, Interview, Offered, Rejected; students see them on `/applications` |
| FR11 auto-close other applications on offer acceptance | `accept_offer` closes every other open application and marks the student Placed |
| FR12 / FR13 / FR14 aptitude tests | `app/aptitude.py`: question bank, timed attempt, auto-grade, random order per attempt |
| FR15 past test scores | `/scores` with a trend chart |
| FR16 / FR17 application summary and score chart | student dashboard (`app/analytics.py`, `app/charts.py`) |
| FR18 / FR19 placement statistics and CSV report | `/admin/analytics`, `/admin/report.csv` |
| NFR2 mobile friendly | responsive layout, tables scroll sideways on phones |
| NFR3 auto-save every 30 seconds | `static/test.js` posts answers to `/attempts/<id>/save` |
| SE-08 / SR6 resume type and size | PDF or DOCX only, 5 MB maximum, file content checked, stored under a random name |
| SR7 correct answers never sent to the browser | the test page query never selects the correct option; answers are shown only after submission |
| SE-06 audit log | applications, status changes, offers, tests and report exports are logged |

## Charts
All charts are drawn on the server as SVG (`app/charts.py`), so they work with the strict Content-Security-Policy and need no JavaScript library: score trend line, application-status donut (student), applications-by-status bars and top-companies bars (Admin).

## Tests
`tests/test_part1.py` (profiles, listings, apply, review, offers), `tests/test_part2.py` (aptitude tests, scores) and `tests/test_part3.py` (charts, analytics, CSV). `tests/test_nfr.py` (health endpoint, WAL mode, concurrent users) was added after Sprint 2. Together with the Sprint 1 tests the suite has 83 tests; all pass (see docs/reports).

## Demo data
`python seed_demo.py` (after `seed_admin.py`) adds an approved demo recruiter, three listings and a 10-question test. Demo recruiter login: `recruiter@demo.com` / `Demo@12345`.

## Deviations from the submitted documents (explain at the final demo)
1. **Emails:** application confirmation, status-change and offer emails are only written to the server log. No mail server is connected.
2. **Test attempts:** there is one open attempt per test at a time. Reopening a test resumes the same attempt so the timer cannot be restarted.
3. **Tests are practice tests** open to every student. The "Test" application status is a label the recruiter sets; it does not unlock a specific test.
4. **Admin creates tests.** Recruiters do not create tests in this version.
5. **Sprint 1 deviations still apply** (session cookie instead of JWT, HTTPS through `COOKIE_SECURE=1`).
6. **Added after Sprint 2 (backlog PRs):** NFR4 concurrency and load test and NFR5 `/health` endpoint (PR #37), NFR7 browser and screen-size check (PR #39). Firefox and Safari have not been tested.
7. **Admin statistics (FR18):** department-wise statistics are not built. The Admin page shows placements, placement percentage, top companies and a status chart; branch appears only in the CSV report.
8. **Question bank (FR12, US-09):** questions have no category and cannot be edited, only added and deleted.
9. **Student charts (FR17):** applications by status are shown as a donut chart, not a funnel chart.

The full list of deviations from the SRS is at the end of SRS_Document.docx.
