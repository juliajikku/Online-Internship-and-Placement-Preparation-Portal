# NFR6 / reporting - Analytics and CSV report

Owner: Julia. Admin analytics page (`/admin/analytics`) shows students, placed, placement rate, recruiters, listings, applications, average test score, charts by status and top companies. `/admin/report.csv` exports applications; cells starting with = + - @ are prefixed with a quote to prevent spreadsheet formula injection. Charts are server-side SVG so they work under the strict Content-Security-Policy. Tests: `tests/test_part3.py`.
