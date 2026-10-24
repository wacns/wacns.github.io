#!/usr/bin/env python3
"""Prints last week's wacns.com report (Markdown) from up to three sources. Each is optional:

- Cloudflare Web Analytics  — env CF_API_TOKEN (API token with Account Analytics: Read)
- Google Analytics 4        — env GOOGLE_SA_KEY (service-account JSON) + GA4_PROPERTY_ID (numeric)
- Google Search Console     — env GOOGLE_SA_KEY + optional GSC_SITE (default "sc-domain:wacns.com")

Sources without credentials are skipped. If none are configured it prints nothing,
so the workflow doesn't post an empty issue. Google sources need: pip install google-auth requests
"""
import datetime as dt, json, os, sys, urllib.parse, urllib.request

CF_ACCOUNT = "b75620a3c29e1be482357fa89021efd5"  # Cloudflare account tag (not secret)
CF_SITE = "d5a54dd3d88949a9ba7c6f03be80b538"     # Web Analytics site tag for wacns.com (not secret)

CF_QUERY = """query($acct: String!, $site: String!, $from: Time!, $to: Time!, $pfrom: Time!) {
  viewer { accounts(filter: {accountTag: $acct}) {
    total: rumPageloadEventsAdaptiveGroups(limit: 1, filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { count sum { visits } }
    prev: rumPageloadEventsAdaptiveGroups(limit: 1, filter: {siteTag: $site, datetime_geq: $pfrom, datetime_lt: $from}) { count sum { visits } }
    pages: rumPageloadEventsAdaptiveGroups(limit: 6, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { count sum { visits } dimensions { requestPath } }
    refs: rumPageloadEventsAdaptiveGroups(limit: 6, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { sum { visits } dimensions { refererHost } }
    countries: rumPageloadEventsAdaptiveGroups(limit: 6, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { sum { visits } dimensions { countryName } }
    devices: rumPageloadEventsAdaptiveGroups(limit: 3, orderBy: [sum_visits_DESC], filter: {siteTag: $site, datetime_geq: $from, datetime_lt: $to}) { sum { visits } dimensions { deviceType } }
  } }
}"""


def md_table(headers, rows):
    if not rows:
        return "_No data_"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] + ["---:"] * (len(headers) - 1)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def trend(now, before):
    if not before:
        return "no data for the week before"
    change = (now - before) / before * 100
    return f"{'▲' if change >= 0 else '▼'} {abs(change):.0f}% vs the week before ({before})"


# ── Cloudflare ────────────────────────────────────────────────────────────────
def cloudflare_fetch(token, start, end, prev_start):
    body = json.dumps({"query": CF_QUERY, "variables": {
        "acct": CF_ACCOUNT, "site": CF_SITE, "from": start.isoformat(), "to": end.isoformat(),
        "pfrom": prev_start.isoformat()}}).encode()
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/graphql", data=body,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError("GraphQL error: " + json.dumps(data["errors"])[:300])
    return data["data"]["viewer"]["accounts"][0]


def cloudflare_section(d):
    visits = lambda rows: rows[0]["sum"]["visits"] if rows else 0
    now, before = visits(d["total"]), visits(d["prev"])
    views = d["total"][0]["count"] if d["total"] else 0
    pick = lambda rows, key, blank="(direct)": [(r["dimensions"][key] or blank, r["sum"]["visits"]) for r in rows if r["sum"]["visits"] > 0]
    return "\n".join([
        "## Cloudflare Web Analytics",
        f"**{now} visits** · {views} page views · {trend(now, before)}",
        "_Every real browser, no cookies; ad blockers don't hide these._\n",
        "**Top pages**\n" + md_table(["Page", "Visits"], pick(d["pages"], "requestPath")) + "\n",
        "**Referrers**\n" + md_table(["Referrer", "Visits"], pick(d["refs"], "refererHost")) + "\n",
        "**Countries**\n" + md_table(["Country", "Visits"], pick(d["countries"], "countryName")) + "\n",
        "**Devices**\n" + md_table(["Device", "Visits"], pick(d["devices"], "deviceType")),
    ])


# ── Google (Analytics 4 + Search Console) ─────────────────────────────────────
def google_session():
    raw = os.environ.get("GOOGLE_SA_KEY", "").strip()
    if not raw:
        return None
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=[
        "https://www.googleapis.com/auth/analytics.readonly",
        "https://www.googleapis.com/auth/webmasters.readonly",
    ])
    return AuthorizedSession(creds)


def ga_report(session, prop, body):
    r = session.post(f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport", json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def ga_section(session, prop, start, end, prev_start, prev_end):
    rng = [{"startDate": start, "endDate": end}, {"startDate": prev_start, "endDate": prev_end}]
    totals = ga_report(session, prop, {
        "dateRanges": rng,
        "metrics": [{"name": n} for n in ("activeUsers", "sessions", "screenPageViews", "averageSessionDuration", "engagementRate")],
    })
    vals = {}
    for row in totals.get("rows", []):
        # With two date ranges GA adds a dateRange dimension: date_range_0 = this week, date_range_1 = the week before
        which = row.get("dimensionValues", [{"value": "date_range_0"}])[0]["value"]
        vals[which] = [float(m["value"]) for m in row["metricValues"]]
    cur, prev = vals.get("date_range_0", [0] * 5), vals.get("date_range_1", [0] * 5)
    users, sessions, views, dur, eng = cur
    pages = ga_report(session, prop, {
        "dateRanges": [rng[0]], "dimensions": [{"name": "pagePath"}], "metrics": [{"name": "screenPageViews"}],
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}], "limit": 6})
    sources = ga_report(session, prop, {
        "dateRanges": [rng[0]], "dimensions": [{"name": "sessionSourceMedium"}], "metrics": [{"name": "sessions"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 6})
    rows = lambda rep: [(r["dimensionValues"][0]["value"], int(float(r["metricValues"][0]["value"]))) for r in rep.get("rows", [])]
    return "\n".join([
        "## Google Analytics",
        f"**{int(users)} users** · {int(sessions)} sessions · {int(views)} page views · "
        f"avg. {int(dur // 60)}m {int(dur % 60)}s per session · {eng * 100:.0f}% engaged · users {trend(int(users), int(prev[0]))}",
        "_Visitors whose browser didn't block Google Analytics._\n",
        "**Top pages**\n" + md_table(["Page", "Views"], rows(pages)) + "\n",
        "**Sources**\n" + md_table(["Source / medium", "Sessions"], rows(sources)),
    ])


def gsc_query(session, site, body):
    url = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(site, safe='')}/searchAnalytics/query"
    r = session.post(url, json=body, timeout=30)
    r.raise_for_status()
    return r.json().get("rows", [])


def gsc_section(session, site, start, end):
    total = gsc_query(session, site, {"startDate": start, "endDate": end})
    queries = gsc_query(session, site, {"startDate": start, "endDate": end, "dimensions": ["query"], "rowLimit": 10})
    pages = gsc_query(session, site, {"startDate": start, "endDate": end, "dimensions": ["page"], "rowLimit": 5})
    t = total[0] if total else {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0}
    fmt = lambda rows: [(r["keys"][0].replace("https://wacns.com", "") or "/", int(r["clicks"]), int(r["impressions"]),
                         f"{r['position']:.1f}") for r in rows]
    return "\n".join([
        "## Google Search",
        f"**{int(t['impressions'])} impressions** · {int(t['clicks'])} clicks · "
        f"{t['ctr'] * 100:.1f}% click rate · average position {t['position']:.1f}" if total else "_No search data yet._",
        "_How often wacns.com appeared in Google results. Google reports this with a 2–3 day delay._\n",
        "**Searches that showed the site**\n" + md_table(["Search", "Clicks", "Impressions", "Avg. position"], fmt(queries)) + "\n",
        "**Pages in search**\n" + md_table(["Page", "Clicks", "Impressions", "Avg. position"], fmt(pages)),
    ])


def main():
    today = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start, prev_start = today - dt.timedelta(days=7), today - dt.timedelta(days=14)
    last_day, prev_last = today - dt.timedelta(days=1), start - dt.timedelta(days=1)
    day = lambda d: d.strftime("%Y-%m-%d")

    sections = []
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if token:
        try:
            sections.append(cloudflare_section(cloudflare_fetch(token, start, today, prev_start)))
        except Exception as e:  # keep the rest of the report
            sections.append(f"## Cloudflare Web Analytics\n_Couldn't load: {e}_")

    session = None
    try:
        session = google_session()
    except Exception as e:
        sections.append(f"## Google\n_Couldn't sign in with GOOGLE_SA_KEY: {e}_")
    if session:
        prop = os.environ.get("GA4_PROPERTY_ID", "").strip()
        if prop:
            try:
                sections.append(ga_section(session, prop, day(start), day(last_day), day(prev_start), day(prev_last)))
            except Exception as e:
                sections.append(f"## Google Analytics\n_Couldn't load: {e}_")
        site = os.environ.get("GSC_SITE", "").strip() or "sc-domain:wacns.com"
        try:
            sections.append(gsc_section(session, site, day(start), day(last_day)))
        except Exception as e:
            sections.append(f"## Google Search\n_Couldn't load: {e}_")

    if not sections:
        print("No sources configured; skipping report.", file=sys.stderr)
        return
    print(f"# wacns.com weekly report: {start:%b %-d} – {last_day:%b %-d, %Y}\n")
    print("\n\n".join(sections))
    print("\ncc @wacns")


if __name__ == "__main__":
    main()
