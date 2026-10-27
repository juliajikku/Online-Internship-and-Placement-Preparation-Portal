# Online Internship and Placement Preparation Portal

#PES1UG24CS203-Joel Thomas
#PES1UG24CS205-Julia Mariam Jikku
#PES1UG25CS842-Juhi Shah


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
