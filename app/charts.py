"""Small server-side SVG charts (no JavaScript, so they work under the strict CSP).

Every label is HTML-escaped. Colours use presentation attributes only.
"""
from markupsafe import Markup, escape

BLUE = "#2e5395"
GRID = "#d5dbe6"
TEXT = "#1c2430"
MUTED = "#5b6677"
STATUS_COLOURS = {
    "Applied": "#6b8cc7", "Shortlisted": "#e0a82e", "Test": "#8e6fc4",
    "Interview": "#2a9d8f", "Offered": "#2e8b57", "Accepted": "#1e6b33",
    "Rejected": "#c0392b", "Closed": "#8a94a6",
}


def _frame(width, height, title, body):
    return Markup(
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}" '
        f'xmlns="http://www.w3.org/2000/svg"><title>{escape(title)}</title>'
        f'<text x="{width / 2}" y="22" text-anchor="middle" font-size="17" font-weight="700" fill="{TEXT}">{escape(title)}</text>'
        f"{body}</svg>"
    )


def _short(label, n=15):
    text = str(label)
    return text if len(text) <= n else text[: n - 1] + "…"


def _empty(width, height, title, message):
    return _frame(width, height, title, f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" font-size="14" fill="{MUTED}">{escape(message)}</text>')


def line_chart(labels, values, title="Trend", ymax=100, width=520, height=300, empty_message="No test attempts yet."):
    """Line chart with dots and value labels; y axis runs 0..ymax."""
    if not values:
        return _empty(width, height, title, empty_message)
    left, right, top, bottom = 48, 20, 40, 44
    pw, ph = width - left - right, height - top - bottom
    parts = []
    for i in range(5):  # horizontal grid + y labels
        y = top + ph - ph * i / 4
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="13" fill="{MUTED}">{round(ymax * i / 4)}</text>')
    n = len(values)
    xs = [left + (pw / 2 if n == 1 else pw * i / (n - 1)) for i in range(n)]
    ys = [top + ph - ph * min(v, ymax) / ymax for v in values]
    parts.append(f'<polyline fill="none" stroke="{BLUE}" stroke-width="2.5" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))}"/>')
    for x, y, v, lab in zip(xs, ys, values, labels):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{BLUE}"/>')
        parts.append(f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{TEXT}">{v}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height - 22}" text-anchor="middle" font-size="13" fill="{MUTED}">{escape(lab)}</text>')
    parts.append(f'<text x="{width / 2}" y="{height - 6}" text-anchor="middle" font-size="13" fill="{MUTED}">Attempt date (month-day)</text>')
    return _frame(width, height, title, "".join(parts))


def bar_chart(items, title="Counts", width=520, height=300, empty_message="No data yet.", colours=None):
    """Vertical bar chart. items = [(label, value), ...]."""
    if not items or not any(v for _, v in items):
        return _empty(width, height, title, empty_message)
    left, right, top, bottom = 36, 14, 44, 54
    pw, ph = width - left - right, height - top - bottom
    vmax = max(v for _, v in items)
    vmax = vmax + (-vmax % 4 or 0) if vmax > 4 else 4  # round the axis top up to a multiple of 4
    parts = []
    for i in range(5):
        y = top + ph - ph * i / 4
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="13" fill="{MUTED}">{round(vmax * i / 4)}</text>')
    slot = pw / len(items)
    bw = min(56, slot * 0.6)
    for i, (label, value) in enumerate(items):
        x = left + slot * i + (slot - bw) / 2
        h = ph * value / vmax
        colour = (colours or {}).get(label, BLUE)
        parts.append(f'<rect x="{x:.1f}" y="{top + ph - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="3" fill="{colour}"/>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{top + ph - h - 6:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{TEXT}">{value}</text>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{height - 26}" text-anchor="middle" font-size="13" fill="{MUTED}">{escape(_short(label))}</text>')
    return _frame(width, height, title, "".join(parts))


def donut_chart(items, title="Share", size=260, empty_message="No data yet."):
    """Donut chart (stroke-dasharray arcs) with a legend. items = [(label, value, colour)]."""
    import math

    total = sum(v for _, v, _ in items)
    if not total:
        return _empty(420, size, title, empty_message)
    cx, cy, r = 110, 150, 70
    circ = 2 * math.pi * r
    parts, offset = [], 0.0
    for label, value, colour in items:
        if not value:
            continue
        frac = value / total
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" stroke-width="34" '
            f'stroke-dasharray="{circ * frac:.2f} {circ:.2f}" stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        offset += circ * frac
    parts.append(f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-size="22" font-weight="700" fill="{TEXT}">{total}</text>')
    y = 80
    for label, value, colour in items:
        parts.append(f'<rect x="230" y="{y - 11}" width="14" height="14" rx="2" fill="{colour}"/>')
        parts.append(f'<text x="252" y="{y}" font-size="13" fill="{TEXT}">{escape(label)}: {value}</text>')
        y += 24
    return _frame(420, max(size, y + 10), title, "".join(parts))
