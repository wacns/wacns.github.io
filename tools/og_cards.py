#!/usr/bin/env python3
"""Generates 1200x630 link-preview cards (og:image) for the TIL index, each TIL entry and the Uses page.

Usage (from the repo root):  python3 tools/og_cards.py .
Needs Python Playwright with Chromium. Reads the TIL list from tools/build_pages.py,
so run it after adding a TIL entry and commit the PNGs it writes.
"""
import ast, html, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")


def til_entries():
    """Pull the NOTES list out of build_pages.py without running it."""
    src = open(os.path.join(ROOT, "tools", "build_pages.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "NOTES" for t in node.targets):
            # Entries are written as dict(key="value", ...), so read their keyword arguments
            return [{kw.arg: ast.literal_eval(kw.value) for kw in call.keywords} for call in node.value.elts]
    raise SystemExit("NOTES not found in build_pages.py")


TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>@font-face{{font-family:Inter;font-weight:100 900;src:url("file://{font}") format("woff2");}}</style>
<style>
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;background:#0a0a0f;font-family:Inter,sans-serif;color:#f0f0f5;position:relative;overflow:hidden;padding:84px 96px}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:56px 56px;-webkit-mask-image:radial-gradient(ellipse 80% 85% at 25% 30%,#000 20%,transparent 75%)}}
.glow{{position:absolute;top:-240px;left:-140px;width:900px;height:640px;background:radial-gradient(closest-side,rgba(138,43,226,.36),transparent);filter:blur(30px)}}
.c{{position:relative;height:100%;display:flex;flex-direction:column}}
.chip{{align-self:flex-start;font-family:'SF Mono','Fira Code',monospace;font-size:24px;color:#b07cf0;background:rgba(138,43,226,.16);border-radius:10px;padding:8px 16px}}
h1{{margin-top:34px;font-size:{size}px;font-weight:700;letter-spacing:-2px;line-height:1.08;max-width:960px;background:linear-gradient(120deg,#fff 40%,#c9a8ff);-webkit-background-clip:text;color:transparent}}
p{{margin-top:22px;font-size:28px;line-height:1.4;color:#9a9aab;max-width:900px}}
.foot{{margin-top:auto;display:flex;align-items:center;justify-content:space-between;font-size:26px;color:#9a9aab}}
.who{{display:flex;align-items:center;gap:16px;color:#f0f0f5;font-weight:600}}
.who img{{width:48px;height:48px}}
</style></head><body>
<div class="grid"></div><div class="glow"></div>
<div class="c">
  <span class="chip">{chip}</span>
  <h1>{title}</h1>
  <p>{summary}</p>
  <div class="foot"><span class="who"><img src="file://{favicon}" alt="">Abdullah · wacns</span><span>{url}</span></div>
</div>
</body></html>"""


def cards():
    yield ("til/og.png", "Today I learned", "Today I Learned",
           "Short notes on things I’ve picked up while building, one idea per entry.", "wacns.com/til")
    for n in til_entries():
        yield (f"til/{n['slug']}/og.png", "TIL · " + n["nice"], n["title"], n["summary"], "wacns.com/til")
    yield ("uses/og.png", "Uses", "What I build with",
           "The languages, data stores and tools I reach for when I build things.", "wacns.com/uses")


def main():
    favicon = os.path.join(ROOT, "favicon.svg")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        for out, chip, title, summary, url in cards():
            size = 76 if len(title) <= 40 else 64 if len(title) <= 60 else 56
            doc = TEMPLATE.format(size=size, chip=html.escape(chip), title=html.escape(title),
                                  summary=html.escape(summary), url=html.escape(url), favicon=favicon,
                                  font=os.path.join(ROOT, "assets", "fonts", "inter-latin-var.woff2"))
            tmp = os.path.join(ROOT, ".og-tmp.html")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(doc)
            page.goto("file://" + tmp)
            page.wait_for_timeout(600)
            dest = os.path.join(ROOT, out)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            page.screenshot(path=dest)
            print("wrote", out)
        os.remove(tmp)
        browser.close()


if __name__ == "__main__":
    main()
