"""Cross-browser and device check for NFR7 and NFR2 (uses Playwright).

For every browser engine that is installed it opens the main pages of each role at
desktop, tablet and phone widths and reports: HTTP status, console errors and
sideways scrolling. Screenshots are saved to browser_check_output/.

Setup (once):   pip install playwright
                playwright install chromium firefox webkit
Run:            python run.py                       (in one terminal)
                python scripts/browser_check.py     (in another)
Optional:       set ADMIN_PASSWORD to include the admin pages
                python scripts/browser_check.py --browsers chromium firefox
It needs the demo recruiter from seed_demo.py (recruiter@demo.com / Demo@12345).
"""
import argparse
import os
import sys
import time

from playwright.sync_api import sync_playwright

PASSWORD = "Check-pass-123"
VIEWPORTS = {"desktop": (1280, 800), "tablet": (768, 1024), "phone": (375, 667)}
PAGES = {
    "public": ["/login", "/register"],
    "student": ["/student", "/student/profile", "/listings", "/applications", "/tests", "/scores"],
    "recruiter": ["/recruiter", "/recruiter/listings", "/recruiter/profile"],
    "admin": ["/admin/", "/admin/tests", "/admin/analytics"],
}


def log_in(page, base, email, password):
    page.goto(base + "/login")
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", password)
    page.click("form.card button[type=submit], form button[type=submit]")
    page.wait_for_load_state("networkidle")
    return "/login" not in page.url


def register_student(page, base, email):
    page.goto(base + "/register")
    page.fill("input[name=name]", "Browser Check")
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", PASSWORD)
    page.select_option("select[name=role]", "student")
    page.click("form button[type=submit]")
    page.wait_for_load_state("networkidle")


def check_page(page, base, path, errors, outdir, tag):
    errors.clear()
    response = page.goto(base + path)
    page.wait_for_load_state("networkidle")
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    name = f"{tag}_{path.strip('/').replace('/', '_') or 'home'}.png"
    page.screenshot(path=os.path.join(outdir, name), full_page=True)
    problems = []
    if response is None or response.status != 200:
        problems.append(f"HTTP {response.status if response else 'none'}")
    if overflow > 1:
        problems.append(f"sideways scroll ({overflow}px)")
    if errors:
        problems.append(f"{len(errors)} console error(s): {errors[0][:80]}")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--browsers", nargs="+", default=["chromium", "firefox", "webkit"])
    args = parser.parse_args()
    outdir = "browser_check_output"
    os.makedirs(outdir, exist_ok=True)
    student_email = f"check{int(time.time())}@test.local"
    roles = {"public": None, "student": (student_email, PASSWORD), "recruiter": ("recruiter@demo.com", "Demo@12345")}
    if os.environ.get("ADMIN_PASSWORD"):
        roles["admin"] = ("admin@portal.local", os.environ["ADMIN_PASSWORD"])
    failures = 0
    registered = []  # the check student is created once, by the first browser that runs
    with sync_playwright() as pw:
        for browser_name in args.browsers:
            try:
                browser = getattr(pw, browser_name).launch()
            except Exception as exc:  # engine not installed
                print(f"{browser_name}: SKIPPED (not installed: {str(exc).splitlines()[0][:60]})")
                continue
            for device, (width, height) in VIEWPORTS.items():
                for role, creds in roles.items():
                    context = browser.new_context(viewport={"width": width, "height": height})
                    page = context.new_page()
                    errors = []
                    page.on("console", lambda m, e=errors: e.append(m.text) if m.type == "error" else None)
                    page.on("pageerror", lambda exc, e=errors: e.append(str(exc)))
                    if creds:
                        if role == "student" and not registered:
                            register_student(page, args.url, creds[0])
                            registered.append(True)
                        if not log_in(page, args.url, *creds):
                            print(f"{browser_name:9}{device:8}{role:10} login FAILED")
                            failures += 1
                            context.close()
                            continue
                    bad = {}
                    for path in PAGES[role]:
                        problems = check_page(page, args.url, path, errors, outdir, f"{browser_name}_{device}_{role}")
                        if problems:
                            bad[path] = problems
                    status = "OK" if not bad else "PROBLEMS"
                    print(f"{browser_name:9}{device:8}{role:10} {len(PAGES[role])} pages  {status}")
                    for path, problems in bad.items():
                        failures += 1
                        print(f"           {path}: {'; '.join(problems)}")
                    context.close()
            browser.close()
    print("\nRESULT:", "PASS" if failures == 0 else f"{failures} problem(s)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
