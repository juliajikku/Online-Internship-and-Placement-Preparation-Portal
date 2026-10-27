# Sprint 1 notes

## What was built
| Backlog item | Issue | What it does |
|---|---|---|
| Use Case: Authenticate User | #1 | Register, log in, role-based dashboards, lockout, logout |
| US-07: Approve recruiter accounts | #9 | Admin queue to approve or reject pending recruiters |

## Requirements covered
| Requirement | Where |
|---|---|
| FR1 register and log in as Student / Recruiter / Admin | `app/auth.py` |
| FR3 recruiter company profile (company name at registration) | `app/auth.py`, `register.html` |
| FR4 Admin approves or rejects recruiters | `app/admin.py` |
| SE-01 authenticate before access | `login_required` in `app/security.py` |
| SE-02 role-based access control | `role_required` in `app/security.py` (403 for wrong role) |
| SE-05 session expiry and secure logout | 30 minute session, POST `/logout` |
| SE-06 audit log | `audit_log` table, `log_action()` |
| SE-08 input validation, XSS, SQL injection | server-side validation, parameterised SQL, auto-escaped templates, CSRF token on every POST |
| SE-10 password hashing | bcrypt |
| SE-12 repeated failed logins | locked for 15 minutes after 5 failures |

## Tests
`tests/test_auth.py` and `tests/test_admin.py` (28 tests) cover registration rules, generic login errors, lockout and unlock, sessions, CSRF, role access, approve/reject and the audit log.

## Deviations from the submitted documents (explain at the final demo)
1. **Session tokens:** the SRS says JWT with expiry. Sprint 1 uses Flask's signed, HttpOnly session cookie with a 30 minute expiry instead. The effect is the same for a single web app.
2. **Lockout email:** the use case says the user is notified by email after 5 failed attempts. Sprint 1 records it in the audit log and server log only. Email sending is not built yet.
3. **HTTPS (SE-04):** HTTPS is a deployment setting. Set `COOKIE_SECURE=1` when the app is served over HTTPS. Local runs use HTTP.
4. **Recruiter posting:** approved recruiters see an "Approved" status. Posting listings is Sprint 2.
