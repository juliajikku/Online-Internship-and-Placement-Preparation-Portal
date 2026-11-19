# Online Internship and Placement Preparation Portal

#PES1UG24CS203-Joel Thomas
#PES1UG24CS205-Julia Mariam Jikku
#PES1UG25CS842-Juhi Shah


## Documents
| Document | Where |
|---|---|
| SRS (v2.0) | `SRS_Document.docx` / `.pdf` |
| SAD | `SAD_Document.docx` / `.pdf` |
| Test Plan (v2.0, 50 test cases) | `Test_Plan_Document.docx` / `.pdf` |
| Backlog and SRS mapping | [docs/BACKLOG.md](docs/BACKLOG.md) |
| Sprint notes | [docs/SPRINT1.md](docs/SPRINT1.md), [docs/SPRINT2.md](docs/SPRINT2.md) |
| Unit, System Validation, Code Coverage, Branch Coverage reports | `docs/reports/` |
| Non-functional results | `docs/nfr/` |
| Demo videos | `sprint1/` and `sprint2 demo/` |

Test results: 83 tests pass (66 unit, 17 system); line coverage 94.8%, branch coverage 85.8%.

## Demo
```bash
python seed_admin.py            # prints the Admin password
python seed_demo.py             # optional demo data
flask --app run run             # http://127.0.0.1:5000
```
Extra scripts in `scripts/`: `load_test.py` (concurrent users), `browser_check.py` (screen sizes, needs Playwright). Health check: `/health`.

## Sprint 2 - Listings, applications, aptitude tests and charts

Adds student and recruiter profiles, listings with search and filters, apply with eligibility checks, applicant review, offer acceptance, timed aptitude tests, score and placement charts and a CSV report.
See [docs/SPRINT2.md](docs/SPRINT2.md). Optional demo data: `python seed_demo.py` (after `seed_admin.py`).

## Sprint 1 - Authentication and recruiter approval

Flask + SQLite web app. Covers the use case **Authenticate User** (issue #1) and **US-07 Approve recruiter accounts** (issue #9).
See [docs/SPRINT1.md](docs/SPRINT1.md) for the requirement mapping and the deviations from the submitted documents.

### Run it locally
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

python seed_admin.py            # creates the Admin and prints a one-time password
flask --app run run             # open http://127.0.0.1:5000
```
Students and recruiters register on the site. Recruiters stay "pending" until the Admin approves them at `/admin/`.

### Run the tests
```bash
pytest -v
```
GitHub Actions runs the same tests on every push and pull request (`.github/workflows/ci.yml`).
