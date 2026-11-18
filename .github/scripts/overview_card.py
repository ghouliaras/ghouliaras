#!/usr/bin/env python3
"""Generate profile overview cards (dark + light) from the GitHub contribution calendar.

Uses only the standard library. The contribution calendar includes private
contributions (as anonymous counts) when "Private contributions" is enabled on
the profile, so the built-in GITHUB_TOKEN is enough — no personal token needed.

Usage: GITHUB_TOKEN=... python3 overview_card.py <username> <out_dir>
       python3 overview_card.py --demo <out_dir>      (render with sample data)
"""
import datetime as dt
import json
import os
import sys
import urllib.request

API = "https://api.github.com/graphql"


def gql(query, token):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-overview-card"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def fetch(username, token):
    base = gql(
        f'''query {{ user(login: "{username}") {{
              createdAt
              repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {{ totalCount }}
              contributionsCollection {{ contributionYears }}
            }} }}''',
        token,
    )["user"]
    years = sorted(base["contributionsCollection"]["contributionYears"])
    parts = []
    for y in years:
        parts.append(
            f'''y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{
                  contributionCalendar {{ weeks {{ contributionDays {{ date contributionCount }} }} }}
                }}'''
        )
    data = gql(f'query {{ user(login: "{username}") {{ {" ".join(parts)} }} }}', token)["user"]
    days = {}
    for y in years:
        for w in data[f"y{y}"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return {"public_repos": base["repositories"]["totalCount"], "days": days}


def compute(days, today=None):
    today = today or dt.date.today()
    dates = sorted(dt.date.fromisoformat(d) for d in days if dt.date.fromisoformat(d) <= today)
    count = {d: days[d.isoformat()] for d in dates}
    total = sum(count.values())
    year_ago = today - dt.timedelta(days=365)
    last_year = sum(c for d, c in count.items() if d > year_ago)

    longest = run = 0
    prev = None
    for d in dates:
        if count[d] > 0:
            run = run + 1 if prev and (d - prev).days == 1 and count.get(prev, 0) > 0 else 1
            longest = max(longest, run)
        prev = d

    # Current streak: today may still be empty without breaking the streak.
    cur = 0
    d = today if count.get(today, 0) > 0 else today - dt.timedelta(days=1)
    while count.get(d, 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)

    best_day = max(count.values()) if count else 0
    return {"total": total, "last_year": last_year, "current": cur, "longest": longest, "best_day": best_day}


def fmt(n):
    return f"{n:,}"


THEMES = {
    "dark": {"title": "#2563EB", "value": "#E6EDF3", "label": "#8B949E", "line": "#30363D"},
    "light": {"title": "#2563EB", "value": "#1F2328", "label": "#57606A", "line": "#D0D7DE"},
}


def svg(stats, public_repos, theme):
    c = THEMES[theme]
    items = [
        (fmt(stats["total"]), "Total contributions"),
        (fmt(stats["last_year"]), "Last 12 months"),
        (f'{stats["current"]} days', "Current streak"),
        (f'{stats["longest"]} days', "Longest streak"),
        (fmt(stats["best_day"]), "Best day"),
        (fmt(public_repos), "Public repositories"),
    ]
    w, h, cols = 840, 150, len(items)
    col_w = w / cols
    cells = []
    for i, (val, label) in enumerate(items):
        x = col_w * i + col_w / 2
        cells.append(
            f'<text x="{x:.1f}" y="88" class="v">{val}</text>'
            f'<text x="{x:.1f}" y="114" class="l">{label}</text>'
        )
        if i:
            cells.append(f'<line x1="{col_w * i:.1f}" y1="64" x2="{col_w * i:.1f}" y2="122" stroke="{c["line"]}"/>')
    updated = dt.date.today().strftime("%d %b %Y")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub contribution overview">
<style>
  .t {{ font: 600 18px 'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif; fill: {c["title"]}; }}
  .u {{ font: 400 11px 'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif; fill: {c["label"]}; }}
  .v {{ font: 700 24px 'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif; fill: {c["value"]}; text-anchor: middle; }}
  .l {{ font: 400 12px 'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif; fill: {c["label"]}; text-anchor: middle; }}
</style>
<text x="24" y="34" class="t">Contribution overview</text>
<text x="{w - 24}" y="34" class="u" text-anchor="end">incl. private work · updated {updated}</text>
{"".join(cells)}
</svg>
'''


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--demo":
        out = sys.argv[2]
        today = dt.date.today()
        days = {(today - dt.timedelta(days=i)).isoformat(): (i * 37) % 90 for i in range(600)}
        data = {"public_repos": 6, "days": days}
    elif len(sys.argv) == 3:
        username, out = sys.argv[1], sys.argv[2]
        token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
        data = fetch(username, token)
    else:
        sys.exit(__doc__)
    stats = compute(data["days"])
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        with open(os.path.join(out, f"overview-{theme}.svg"), "w", encoding="utf-8") as f:
            f.write(svg(stats, data["public_repos"], theme))
    print(json.dumps({**stats, "public_repos": data["public_repos"]}))


if __name__ == "__main__":
    main()
