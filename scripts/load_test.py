"""Simple load test for NFR4 (100 to 200 concurrent users) and NFR1 (pages load within 3 s).

Uses only the Python standard library. Every virtual user logs in as a student, then
opens the main pages several times. Latency and errors are summarised at the end.

  1. Create test accounts (run in the project folder, with the app stopped or running):
         python scripts/load_test.py --seed 150
  2. Start the app in another terminal:   python run.py
  3. Run the test:
         python scripts/load_test.py --users 150 --rounds 5 --ramp 5

--ramp is the number of seconds over which the users arrive (0 = everyone at once).
Test accounts are load0@test.local ... with the password below. Delete the instance
folder afterwards if you do not want them in your demo data.
"""
import argparse
import http.cookiejar
import os
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

PASSWORD = "Load-test-pass-1"
PAGES = ["/student", "/listings", "/applications", "/tests", "/scores"]
CSRF = re.compile(r'name="csrf_token" value="([0-9a-f]+)"')

lock = threading.Lock()
samples = []  # (page, seconds, ok)


def record(page, started, ok):
    with lock:
        samples.append((page, time.perf_counter() - started, ok))


def fetch(opener, base, path, data=None):
    started = time.perf_counter()
    try:
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        with opener.open(urllib.request.Request(base + path, data=body), timeout=60) as resp:
            html = resp.read().decode("utf-8", "replace")
            record(path if data is None else "POST " + path, started, resp.status == 200)
            return html
    except (urllib.error.URLError, TimeoutError, OSError):
        record(path if data is None else "POST " + path, started, False)
        return ""


def virtual_user(base, n, rounds, delay):
    time.sleep(delay)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    html = fetch(opener, base, "/login")
    match = CSRF.search(html)
    if not match:
        return
    fetch(opener, base, "/login", {"csrf_token": match.group(1), "email": f"load{n}@test.local", "password": PASSWORD})
    for _ in range(rounds):
        for page in PAGES:
            fetch(opener, base, page)
            time.sleep(0.05)


def seed(count):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
    import bcrypt

    from app import create_app
    from app.db import get_db, utcnow

    app = create_app()
    hashed = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt())  # same hashing cost as real accounts
    added = 0
    with app.app_context():
        db = get_db()
        for n in range(count):
            email = f"load{n}@test.local"
            if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
                continue
            db.execute(
                "INSERT INTO users (name, email, password_hash, role, status, created_at) VALUES (?, ?, ?, 'student', 'active', ?)",
                (f"Load User {n}", email, hashed, utcnow().isoformat()),
            )
            added += 1
        db.commit()
    print(f"Seeded {added} new test students (total requested {count}).")


def percentile(values, pct):
    values = sorted(values)
    return values[min(len(values) - 1, int(len(values) * pct / 100))] if values else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--users", type=int, default=150)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--ramp", type=float, default=5.0)
    parser.add_argument("--seed", type=int, metavar="N", help="create N test students and exit")
    args = parser.parse_args()
    if args.seed:
        seed(args.seed)
        return 0

    start = time.perf_counter()
    threads = [
        threading.Thread(target=virtual_user, args=(args.url, n, args.rounds, args.ramp * n / max(args.users, 1)))
        for n in range(args.users)
    ]
    [t.start() for t in threads]
    [t.join() for t in threads]
    elapsed = time.perf_counter() - start

    total = len(samples)
    failed = sum(1 for _, _, ok in samples if not ok)
    print(f"\n{args.users} concurrent users, {args.rounds} rounds each, ramp {args.ramp:g}s")
    print(f"{total} requests in {elapsed:.1f}s ({total / elapsed:.1f} requests/s), {failed} failed ({100 * failed / max(total, 1):.2f}%)")
    print(f"{'page':<18}{'count':>7}{'avg s':>9}{'p95 s':>9}{'max s':>9}")
    pages = sorted({p for p, _, _ in samples})
    for page in pages:
        times = [t for p, t, _ in samples if p == page]
        print(f"{page:<18}{len(times):>7}{statistics.mean(times):>9.3f}{percentile(times, 95):>9.3f}{max(times):>9.3f}")
    page_times = [t for p, t, _ in samples if not p.startswith("POST")]
    p95 = percentile(page_times, 95)
    print(f"\nAll page views: p95 = {p95:.3f}s (NFR1 target: under 3 s)")
    print("RESULT:", "PASS" if failed == 0 and p95 < 3 else "FAIL")
    return 0 if failed == 0 and p95 < 3 else 1


if __name__ == "__main__":
    sys.exit(main())
