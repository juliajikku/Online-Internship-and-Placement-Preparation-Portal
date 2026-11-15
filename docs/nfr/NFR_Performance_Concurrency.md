# NFR1 / NFR4 / NFR5 - Performance, concurrency and availability

Owner: Joel. Measured on a 2-core cloud machine that also ran the load generator, using the Flask development server (a production server would do better).

## What was built
- `app/db.py`: SQLite opened with `timeout=10`, WAL journal mode and `busy_timeout=10000`, so many users can read while one writes without "database is locked" errors (NFR4).
- `app/health.py`: `GET /health` runs `SELECT 1`; returns 200 `{"status":"ok"}` or 503 when the database is unreachable (NFR5 monitoring hook).
- `scripts/load_test.py`: standard-library thread load test. `python scripts/load_test.py --seed 150` then `python scripts/load_test.py --users 150 --ramp 30`.
- `tests/test_nfr.py`: health OK, health 503, WAL + busy_timeout set, 20 simultaneous users login and browse.

## Measured results
| Scenario | Failed requests | Page-view p95 | Note |
|---|---|---|---|
| 150 users, ramp 30 s | 0 | 0.026 s | POST /login p95 1.2 s |
| 150 users, ramp 5 s | 0 | 1.31 s | /student p95 3.2 s |
| 200 users at once | 0 | 1.59 s | POST /login about 28 s |

Login is slow under a burst on purpose: bcrypt cost 12 protects passwords (security requirement). Page views stay fast.

## Honest limits
- Numbers come from one machine with the load generator on it; they are indicative, not a formal benchmark.
- 200 simultaneous logins in one instant is slow at login; a real deployment would use more CPU cores and a production WSGI server.
