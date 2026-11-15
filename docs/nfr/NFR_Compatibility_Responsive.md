# NFR7 - Browser and device compatibility

Owner: Juhi. Tool: `scripts/browser_check.py` (Playwright).

Run: `pip install playwright` then `playwright install chromium firefox webkit`, start the app, then
`python scripts/browser_check.py --browsers chromium firefox webkit` (set `ADMIN_PASSWORD` for the admin pages).

It opens public, student, recruiter and admin pages at desktop (1280x800), tablet (768x1024) and phone (375x667) sizes and checks: HTTP 200, no console errors, no sideways scrolling. Screenshots go to `browser_check_output/`.

## Result so far
- Chromium: all roles, all three sizes - OK, no overflow, no console errors.
- Firefox and Safari (WebKit): NOT yet run - to be run on a machine that has them and the result added here.
