#!/usr/bin/env python3
"""Prints last week's wacns.com visitor report (Markdown) from Cloudflare Web Analytics.

Env: CF_API_TOKEN — Cloudflare API token with Account Analytics: Read.
Without a token it prints nothing (so the workflow skips posting).
"""
import datetime as dt, json, os, sys, urllib.request

ACCOUNT = "b75620a3c29e1be482357fa89021efd5"  # Cloudflare account tag (not secret)
SITE = "d5a54dd3d88949a9ba7c6f03be80b538"     # Web Analytics site tag for wacns.com (not secret)

QUERY = """query($acct: String!, $site: String!, $from: Time!, $to: Time!, $pfrom: Time!) {
  viewer { accounts(filter: {accountTag: $acct}) {
    total: rumPageloadEventsAdaptiveGroups(limit: 1, filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { count sum { visits } }
    prev: rumPageloadEventsAdaptiveGroups(limit: 1, filter: {siteTag: $site, datetime_geq: $pfrom, datetime_lt: $from}) { count sum { visits } }
    pages: rumPageloadEventsAdaptiveGroups(limit: 6, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { count sum { visits } dimensions { requestPath } }
    refs: rumPageloadEventsAdaptiveGroups(limit: 6, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { sum { visits } dimensions { refererHost } }
    countries: rumPageloadEventsAdaptiveGroups(limit: 6, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { sum { visits } dimensions { countryName } }
    devices: rumPageloadEventsAdaptiveGroups(limit: 3, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { sum { visits } dimensions { deviceType } }
  } }
}"""


def fetch(token, start, end, prev_start):
    body = json.dumps({"query": QUERY, "variables": {
        "acct": ACCOUNT, "site": SITE, "from": start.isoformat(), "to": end.isoformat(), "pfrom": prev_start.isoformat()}}).encode()
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/graphql", data=body,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise SystemExit("GraphQL error: " + json.dumps(data["errors"])[:500])
    return data["data"]["viewer"]["accounts"][0]


def visits(rows):
    return rows[0]["sum"]["visits"] if rows else 0


def table(rows, key, label, blank="(direct / none)"):
    lines = [f"| {label} | Visits |", "|---|---:|"]
    for r in rows:
        if r["sum"]["visits"] <= 0:
            continue
        lines.append(f"| {r['dimensions'][key] or blank} | {r['sum']['visits']} |")
    return "\n".join(lines) if len(lines) > 2 else "_No data_"


def main():
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not token:
        print("CF_API_TOKEN not set; skipping report.", file=sys.stderr)
        return
    today = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start, prev_start = today - dt.timedelta(days=7), today - dt.timedelta(days=14)
    d = fetch(token, start, today, prev_start)

    now, before = visits(d["total"]), visits(d["prev"])
    views = d["total"][0]["count"] if d["total"] else 0
    if before:
        change = (now - before) / before * 100
        trend = f"{'▲' if change >= 0 else '▼'} {abs(change):.0f}% vs the week before ({before})"
    else:
        trend = "no data for the week before"
    last_day = today - dt.timedelta(days=1)
    span = f"{start:%b %-d} – {last_day:%b %-d, %Y}"

    print(f"# wacns.com visitors: {span}\n")
    print(f"**{now} visits** · {views} page views · {trend}\n")
    print("Real browsers only (Cloudflare Web Analytics), so bots and scanners aren't counted.\n")
    print("### Top pages\n" + table(d["pages"], "requestPath", "Page") + "\n")
    print("### Where visitors came from\n" + table(d["refs"], "refererHost", "Referrer") + "\n")
    print("### Countries\n" + table(d["countries"], "countryName", "Country") + "\n")
    print("### Devices\n" + table(d["devices"], "deviceType", "Device") + "\n")
    print("cc @wacns")


if __name__ == "__main__":
    main()
