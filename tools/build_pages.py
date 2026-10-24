#!/usr/bin/env python3
"""Generates the shared-layout pages of wacns.com (homepage EN/AR, TIL, uses).

Usage (from the repo root):  python3 tools/build_pages.py .
The output is plain HTML that gets committed; there is no build step on deploy."""
import os, sys, html, json

OUT = sys.argv[1]
LINKEDIN = "https://www.linkedin.com/in/abdullah-mohammed-137928219"
GITHUB = "https://github.com/wacns"

GH_SVG = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.590.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'
LI_SVG = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M0 1.15C0 .52.52 0 1.17 0h13.66C15.48 0 16 .52 16 1.15v13.7c0 .63-.52 1.15-1.17 1.15H1.17C.52 16 0 15.48 0 14.85V1.15zM4.75 13.4V6.17H2.35v7.23h2.4zM3.55 5.18c.84 0 1.36-.56 1.36-1.25-.02-.71-.52-1.25-1.34-1.25-.82 0-1.36.54-1.36 1.25 0 .7.52 1.25 1.33 1.25h.01zM8.48 13.4V9.36c0-.22.02-.43.08-.58.17-.43.57-.88 1.23-.88.87 0 1.22.66 1.22 1.64v3.86h2.4V9.26c0-2.22-1.18-3.25-2.76-3.25-1.27 0-1.84.7-2.16 1.2v.02h-.02l.02-.02V6.17h-2.4c.03.68 0 7.23 0 7.23h2.4z"/></svg>'
GH_SVG = GH_SVG.replace("-1.590.82", "-1.59.82")

import hashlib
def _ver(rel):
    """Short content hash so long-cached assets refresh as soon as they change."""
    with open(os.path.join(OUT, rel), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]
CSS_URL = "/assets/site.css?v=" + _ver("assets/site.css")
JS_URL = "/assets/site.js?v=" + _ver("assets/site.js")

THEME_BOOT = ("<script>(function(){"
              # The GitHub Pages mirror sends visitors to the main domain, same path
              "if(/\\.github\\.io$/.test(location.hostname)){location.replace('https://wacns.com'+location.pathname+location.search+location.hash);return;}"
              "var d=document.documentElement,t=null;d.classList.add('js');"
              "try{t=localStorage.getItem('theme');}catch(e){}"
              "if(t!=='light'&&t!=='dark'){t=window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';}"
              "d.setAttribute('data-theme',t);"
              "try{if(localStorage.getItem('intro')==='long')d.setAttribute('data-intro','long');}catch(e){}"
              "})();</script>")

S = {
  "en": dict(skip="Skip to content", palette="Search and commands", theme="Switch theme", lang_label="العربية", lang_href="/ar/",
             lang_aria="Read this page in Arabic", site="Site", elsewhere="Elsewhere", projects="Projects", notes="TIL",
             uses="Uses", about_short="Backend developer in Manama, Bahrain.", colophon="Plain HTML &amp; CSS, served by Cloudflare Workers",
             home="Home", palette_label="Command palette",
             privacy="Privacy", cookie_settings="Cookie settings",
             consent_label="Cookie consent",
             consent_text="I use Google Analytics to see which pages are useful. It sets cookies, so it only runs if you allow it.",
             accept="Allow", decline="No thanks"),
  "ar": dict(skip="انتقل إلى المحتوى", palette="البحث والأوامر", theme="تبديل المظهر", lang_label="EN", lang_href="/",
             lang_aria="Read this page in English", site="الموقع", elsewhere="في مكان آخر", projects="المشاريع", notes="تعلّمت اليوم",
             uses="أدواتي", about_short="مطوّر أنظمة خلفية في المنامة، البحرين.", colophon="HTML و CSS بسيطة، تُقدَّم عبر Cloudflare Workers",
             home="الرئيسية", palette_label="لوحة الأوامر",
             privacy="الخصوصية", cookie_settings="إعدادات ملفات تعريف الارتباط",
             consent_label="الموافقة على ملفات تعريف الارتباط",
             consent_text="أستخدم Google Analytics لمعرفة الصفحات المفيدة. يضع ملفات تعريف ارتباط، لذلك لا يعمل إلا إذا سمحت بذلك.",
             accept="سماح", decline="لا، شكرًا"),
}

def head(lang, title, desc, path, extra="", alternates=None, og=True, og_image="/og.png", canonical=True, robots=None):
    url = "https://wacns.com" + path
    dirattr = ' dir="rtl"' if lang == "ar" else ""
    preload = '<link rel="preload" href="/assets/fonts/inter-latin-var.woff2" as="font" type="font/woff2" crossorigin>'
    if lang == "ar":
        preload += '\n  <link rel="preload" href="/assets/fonts/plex-arabic-400.woff2" as="font" type="font/woff2" crossorigin>'
    alt = ""
    if alternates:
        alt = "".join(f'\n  <link rel="alternate" hreflang="{hl}" href="https://wacns.com{p}">' for hl, p in alternates)
    ogt = ""
    if og:
        ogt = f"""
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="https://wacns.com{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">"""
    return f"""<!DOCTYPE html>
<html lang="{lang}"{dirattr}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="theme-color" content="#0a0a0f">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  {f'<link rel="canonical" href="{url}">' if canonical else ''}{f'<meta name="robots" content="{robots}">' if robots else ''}{alt}{ogt}
  {THEME_BOOT}
  {preload}
  <link rel="stylesheet" href="{CSS_URL}">{extra}
</head>"""

def topbar(lang, nav, brand_href, lang_href=None):
    s = S[lang]
    links = "\n".join(
        f'        <a href="{h}"{" class=\"opt\"" if opt else ""}>{t}</a>' for t, h, opt in nav)
    lh = lang_href or s["lang_href"]
    return f"""  <a class="skip-link" href="#content">{s['skip']}</a>
  <header class="topbar" id="topbar">
    <div class="wrap">
      <a class="brand" href="{brand_href}"><img src="/favicon.svg" alt="">wacns</a>
      <div class="topbar-right">
        <nav class="topnav" aria-label="{'الأقسام' if lang == 'ar' else 'Sections'}">
{links}
        </nav>
        <button type="button" class="icon-btn" id="paletteBtn" aria-label="{s['palette']}" aria-haspopup="dialog">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><kbd>Ctrl K</kbd>
        </button>
        <button type="button" class="icon-btn" id="themeBtn" aria-label="{s['theme']}">
          <svg class="theme-dark-only" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
          <svg class="theme-light-only" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        </button>
        <a class="icon-btn" href="{lh}" hreflang="{'en' if lang == 'ar' else 'ar'}" aria-label="{s['lang_aria']}" lang="{'en' if lang == 'ar' else 'ar'}">{s['lang_label']}</a>
      </div>
    </div>
  </header>"""

def palette(lang):
    s = S[lang]
    return f"""  <div class="palette" id="palette" role="dialog" aria-modal="true" aria-label="{s['palette_label']}" hidden>
    <div class="palette-box">
      <input class="palette-input" type="text" role="combobox" aria-expanded="true" aria-controls="paletteList" aria-autocomplete="list" aria-label="{s['palette']}" autocomplete="off" spellcheck="false">
      <!-- [html-validate-disable-next prefer-native-element -- filterable command list; a native select can't type-to-filter] -->
      <ul class="palette-list" id="paletteList" role="listbox" aria-label="{s['palette']}"></ul>
      <div class="palette-hint" aria-hidden="true"></div>
    </div>
  </div>
  <div class="toast" id="toast" role="status" aria-live="polite"></div>
  <section class="consent" id="consent" aria-label="{s['consent_label']}" hidden>
    <p>{s['consent_text']} <a href="/privacy/">{s['privacy']}</a></p>
    <div class="consent-actions">
      <button type="button" class="btn btn-ghost" data-consent="denied">{s['decline']}</button>
      <button type="button" class="btn btn-ghost" data-consent="granted">{s['accept']}</button>
    </div>
  </section>"""

def footer(lang, home):
    s = S[lang]
    return f"""  <footer>
    <div class="wrap">
      <div class="footer-grid">
        <div class="footer-about">
          <a class="brand" href="{home}"><img src="/favicon.svg" alt="">wacns</a>
          <p>{s['about_short']}</p>
        </div>
        <div class="footer-col">
          <h3>{s['site']}</h3>
          <ul>
            <li><a href="{home}#projects">{s['projects']}</a></li>
            <li><a href="/til/">{s['notes']}</a></li>
            <li><a href="/uses/">{s['uses']}</a></li>
            <li><a href="{s['lang_href']}" lang="{'en' if lang == 'ar' else 'ar'}" hreflang="{'en' if lang == 'ar' else 'ar'}">{'English' if lang == 'ar' else 'العربية'}</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>{s['elsewhere']}</h3>
          <ul>
            <li><a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a></li>
            <li><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 wacns · <a href="/privacy/">{s['privacy']}</a><button type="button" class="link-btn" id="cookieSettings" hidden> · {s['cookie_settings']}</button></span>
        <span class="colophon">{s['colophon']}<br><span id="lastDeploy" hidden></span></span>
      </div>
    </div>
  </footer>"""

TAIL = f"""
  <script src="{JS_URL}" defer></script>
</body>
</html>
"""

def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    content = "\n".join(line.rstrip() for line in content.split("\n"))
    while "\n\n\n" in content:
        content = content.replace("\n\n\n", "\n\n")
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

def code_card(filename, code_html):
    return f"""<div class="code-card">
        <div class="code-bar" aria-hidden="true"><i></i><i></i><i></i><span>{filename}</span></div>
<pre><code>{code_html}</code></pre>
      </div>"""

def tk(cls, txt): return f'<span class="tk-{cls}">{html.escape(txt)}</span>'

# ───────────────────────── About code (shared by both languages)
def about_code(lang):
    comment = "// What I care about"
    focus = ['"fast queries"', '"clean APIs"', '"integrations that just work"']
    P = lambda t: tk("pu", t)
    def arr(items): return P("[") + (P(", ")).join(tk("str", i) for i in items) + P("]")
    lines = [
        f'{tk("kw","var")} abdullah {P("=")} {tk("kw","new")} {tk("ty","Developer")}',
        P("{"),
        f'    {tk("pr","Handle")}   {P("=")} {tk("str", chr(34)+"wacns"+chr(34))}{P(",")}',
        f'    {tk("pr","Role")}     {P("=")} {tk("str", chr(34)+"Backend Developer"+chr(34))}{P(",")}',
        f'    {tk("pr","Location")} {P("=")} {tk("str", chr(34)+"Manama, Bahrain"+chr(34))}{P(",")}',
        "",
        f'    {tk("pr","Backend")}  {P("=")} {arr([chr(34)+x+chr(34) for x in ["C#", "ASP.NET Core", "Node.js", "REST APIs"]])}{P(",")}',
        f'    {tk("pr","Data")}     {P("=")} {arr([chr(34)+x+chr(34) for x in ["MySQL", "MongoDB", "Supabase"]])}{P(",")}',
        f'    {tk("pr","Tooling")}  {P("=")} {arr([chr(34)+x+chr(34) for x in ["Docker", "GitHub Actions", "Cloudflare Workers", "Puppeteer"]])}{P(",")}',
        "",
        f'    {tk("cm", comment)}',
        f'    {tk("pr","Focus")}    {P("=")} {arr(focus)}{P(",")}',
        P("};"),
    ]
    return code_card("Abdullah.cs", "\n".join(lines))

# ───────────────────────── TIL entries (newest first)
NOTES = [
  dict(slug="bdi-rtl", date="2026-10-24", nice="Oct 24, 2026",
       title="<bdi> stops .NET from turning into NET. in Arabic text",
       summary="Why Latin terms with punctuation flip inside right-to-left text, and the one-element fix."),
  dict(slug="worker-subdomain-catch-all", date="2026-10-24", nice="Oct 24, 2026",
       title="One Worker, one site, and a 404 for every unknown subdomain",
       summary="Wildcard DNS, routes with no Worker attached, and run_worker_first."),
  dict(slug="assetsignore", date="2026-10-23", nice="Oct 23, 2026",
       title=".assetsignore decides what a Cloudflare Worker publishes",
       summary="Everything in the assets directory goes live, dot-folders included. One file controls it."),
]
TIL = {n["slug"]: n for n in NOTES}

def notes_list(limit=None, lang="en", dates=True):
    items = NOTES[:limit] if limit else NOTES
    out = []
    for n in items:
        attr = ' lang="en" dir="ltr"' if lang == "ar" else ""
        out.append(f"""        <li{attr}><a href="/til/{n['slug']}/">
          {f'<time class="note-date" datetime="{n["date"]}">{n["nice"]}</time>' if dates else ''}
          <span><span class="note-title">{html.escape(n['title'])}</span><span class="note-sum">{html.escape(n['summary'])}</span></span>
        </a></li>""")
    return "\n".join(out)

# ───────────────────────── Homepage
HOME = {
 "en": dict(
   title="Abdullah — Backend Developer",
   desc="Abdullah (wacns) — backend developer in Manama, Bahrain. .NET, C#, MySQL and integrations.",
   role="Backend Developer · Manama, Bahrain",
   toggle=("Short", "Long"), toggle_label="Intro length",
   short='I build backend systems in .NET and C#, tune MySQL queries <mark>until they’re fast</mark>, and connect platforms that <mark>weren’t designed to talk to each other</mark>.',
   long=['I’m Abdullah, a backend developer based in Manama, Bahrain. Most of my days are spent in C# and ASP.NET Core: designing APIs, <mark>tracking down the MySQL queries</mark> that slow down once real data piles up, and generating the Word and Excel reports people actually rely on.',
         'Outside of that I build my own things: a cross-platform finance app, automations that run on a schedule, and small services on Cloudflare Workers. Mostly to scratch an itch, and <mark>to learn something new</mark> along the way.'],
   see="See projects", stats=("contributions this year", "projects", "On GitHub since"), stats_label="At a glance",
   nav=[("Now", "#now", True), ("Projects", "#projects", False), ("Activity", "#activity", True), ("TIL", "#til", False), ("About", "#about", False)],
   now="Now", now_items=["Shipping FinancialAdvisor 1.7: an AI assistant with flexible funding options and a deeper budgeting toolkit.",
                         "Building small tools and dashboards on Cloudflare Workers for my own projects.",
                         "Rebuilding this site, one detail at a time."],
   now_updated="Updated October 2026",
   projects="Projects",
   cards=[("wacns/financial-advisor-releases", "FinancialAdvisor", "Personal finance and budgeting app with an AI assistant. Ships for Android, iOS, Windows, macOS and Linux with built-in desktop auto-updates.", ["Cross-platform", "Supabase", "AI"]),
          ("wacns/api.garagecom", "Garagecom API", "Backend for Garagecom, a car-owner and garage app. Controllers, middleware and filters on ASP.NET Core, packaged with Docker.", ["C#", "ASP.NET Core", "Docker"]),
          ("wacns/8bp-free-gift-collector", "8 Ball Pool Gift Collector", "Collects the free daily gifts from the 8 Ball Pool web shop on a schedule and logs every reward to an archive.", ["Puppeteer", "GitHub Actions"]),
          ("wacns/AutoStore-WACNS", "AutoStore", "Discord storefront bot with products, stock, user balances and payment handling, all managed through slash commands.", ["Node.js", "discord.js", "MongoDB"])],
   activity="Activity", activity_total="contributions on GitHub in the last year", graph_label="GitHub contribution graph for the last year",
   less="Less", more="More",
   notes="Today I learned", all_notes="All entries →", notes_note="",
   about="About",
   cta="Let’s build something.", cta_sub="Always happy to talk backend, APIs and integrations.", cta_btn="Message me on LinkedIn",
 ),
 "ar": dict(
   title="عبدالله — مطوّر أنظمة خلفية",
   desc="عبدالله (wacns) — مطوّر أنظمة خلفية في المنامة، البحرين. ‎.NET و C# و MySQL والتكاملات.",
   role="مطوّر أنظمة خلفية · المنامة، البحرين",
   toggle=("مختصر", "مفصّل"), toggle_label="طول التعريف",
   short='أبني أنظمة خلفية باستخدام <bdi>.NET</bdi> و <bdi>C#</bdi>، وأحسّن استعلامات MySQL <mark>حتى تصبح سريعة</mark>، وأربط منصّات <mark>لم تُصمَّم لتتحدّث مع بعضها</mark>.',
   long=['أنا عبدالله، مطوّر أنظمة خلفية مقيم في المنامة، البحرين. أقضي معظم وقتي مع <bdi>C#</bdi> و <bdi>ASP.NET Core</bdi>: أصمّم واجهات برمجية، <mark>وأتتبّع استعلامات MySQL</mark> التي تبطؤ مع تراكم البيانات الحقيقية، وأولّد تقارير Word و Excel يعتمد عليها الناس فعلًا.',
         'وخارج ذلك أبني مشاريعي الخاصة: تطبيق مالي يعمل على عدة منصّات، وأتمتة تعمل وفق جدول زمني، وخدمات صغيرة على Cloudflare Workers. غالبًا لأحلّ مشكلة تزعجني، <mark>ولأتعلّم شيئًا جديدًا</mark> في الطريق.'],
   see="شاهد المشاريع", stats=("مساهمة هذا العام", "مشاريع", "على GitHub منذ"), stats_label="نظرة سريعة",
   nav=[("الآن", "#now", True), ("المشاريع", "#projects", False), ("النشاط", "#activity", True), ("تعلّمت", "#til", False), ("نبذة", "#about", False)],
   now="الآن", now_items=["أطلق الإصدار 1.7 من FinancialAdvisor: مساعد ذكي بخيارات تمويل مرنة وأدوات ميزانية أعمق.",
                          "أبني أدوات ولوحات صغيرة على Cloudflare Workers لمشاريعي الخاصة.",
                          "أعيد بناء هذا الموقع، تفصيلةً تلو الأخرى."],
   now_updated="آخر تحديث: أكتوبر 2026",
   projects="المشاريع",
   cards=[("wacns/financial-advisor-releases", "FinancialAdvisor", "تطبيق للتمويل الشخصي والميزانية مع مساعد ذكي. يعمل على Android و iOS و Windows و macOS و Linux مع تحديثات تلقائية لنسخ سطح المكتب.", ["Cross-platform", "Supabase", "AI"]),
          ("wacns/api.garagecom", "Garagecom API", "الواجهة الخلفية لتطبيق Garagecom الذي يجمع أصحاب السيارات بالكراجات. وحدات تحكّم وبرمجيات وسيطة وفلاتر على <bdi>ASP.NET Core</bdi>، ومغلّفة بـ Docker.", ["C#", "ASP.NET Core", "Docker"]),
          ("wacns/8bp-free-gift-collector", "8 Ball Pool Gift Collector", "يجمع الهدايا اليومية المجانية من متجر 8 Ball Pool على الويب وفق جدول زمني، ويسجّل كل مكافأة في أرشيف.", ["Puppeteer", "GitHub Actions"]),
          ("wacns/AutoStore-WACNS", "AutoStore", "بوت متجر على Discord للمنتجات والمخزون وأرصدة المستخدمين ومعالجة المدفوعات، ويُدار بالكامل عبر أوامر الشَّرطة المائلة.", ["Node.js", "discord.js", "MongoDB"])],
   activity="النشاط", activity_total="مساهمة على GitHub خلال العام الماضي", graph_label="مخطط مساهمات GitHub خلال العام الماضي",
   less="أقل", more="أكثر",
   notes="تعلّمت اليوم", all_notes="كل التدوينات ←", notes_note='<p class="notes-lang">التدوينات مكتوبة بالإنجليزية.</p>',
   about="نبذة",
   cta="لنبنِ شيئًا معًا.", cta_sub="يسعدني دائمًا الحديث عن الأنظمة الخلفية والواجهات البرمجية والتكاملات.", cta_btn="راسلني على LinkedIn",
 ),
}

JSONLD = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Person",
        "@id": "https://wacns.com/#person",
        "name": "Abdullah",
        "alternateName": "wacns",
        "url": "https://wacns.com/",
        "image": "https://wacns.com/og.png",
        "jobTitle": "Backend Developer",
        "address": { "@type": "PostalAddress", "addressLocality": "Manama", "addressCountry": "BH" },
        "knowsAbout": ["C#", "ASP.NET Core", "Node.js", "MySQL", "MongoDB", "REST APIs", "Cloudflare Workers", "Docker"],
        "sameAs": [
          "https://github.com/wacns",
          "https://www.linkedin.com/in/abdullah-mohammed-137928219"
        ]
      },
      {
        "@type": "WebSite",
        "@id": "https://wacns.com/#website",
        "url": "https://wacns.com/",
        "name": "wacns",
        "inLanguage": ["en", "ar"],
        "author": { "@id": "https://wacns.com/#person" }
      }
    ]
  }
  </script>"""

def homepage(lang):
    h = HOME[lang]
    path = "/" if lang == "en" else "/ar/"
    home = path
    cards = "\n".join(f"""        <article class="card reveal" data-repo="{repo}">
          <h3 class="card-title" lang="en" dir="auto">{name}</h3>
          <p class="card-desc">{desc}</p>
          <ul class="tags" lang="en">{''.join(f'<li>{t}</li>' for t in tags)}</ul>
          <p class="card-meta"></p>
        </article>""" for repo, name, desc, tags in h["cards"])
    long_html = "\n      ".join(f'<p class="intro" data-intro-text="long" hidden>{p}</p>' for p in h["long"])
    now_items = "\n".join(f"          <li>{t}</li>" for t in h["now_items"])
    body = f"""
<body>
  <div class="hero-fx" aria-hidden="true"><div class="hero-bg"></div><div class="hero-glow"></div></div>
{topbar(lang, h['nav'], '#top')}

  <main id="content">
    <div class="hero wrap" id="top">
      <p class="handle" dir="ltr">@wacns</p>
      <h1>{'عبدالله' if lang == 'ar' else 'Abdullah'}</h1>
      <p class="role">{h['role']}</p>
      <div class="intro-toggle" id="introToggle" role="group" aria-label="{h['toggle_label']}">
        <button type="button" data-intro="short" aria-pressed="true">{h['toggle'][0]}</button>
        <button type="button" data-intro="long" aria-pressed="false">{h['toggle'][1]}</button>
      </div>
      <p class="intro" data-intro-text="short">{h['short']}</p>
      {long_html}
      <div class="links">
        <a class="btn btn-primary" href="{GITHUB}" target="_blank" rel="noopener">{GH_SVG} GitHub</a>
        <a class="btn btn-ghost" href="{LINKEDIN}" target="_blank" rel="noopener">{LI_SVG} LinkedIn</a>
        <a class="btn btn-ghost" href="#projects">{h['see']}</a>
      </div>
      <ul class="stats" aria-label="{h['stats_label']}">
        <li id="statContrib" class="pending"><strong id="statContribN">000</strong> {h['stats'][0]}</li>
        <li><strong id="statProjects">{len(h['cards'])}</strong> {h['stats'][1]}</li>
        <li id="statSince" class="pending">{h['stats'][2]} <strong id="statSinceN">0000</strong></li>
      </ul>
    </div>

    <div class="band alt"><section class="wrap reveal" id="now" aria-labelledby="now-heading">
      <h2 id="now-heading"><span class="pulse" aria-hidden="true"></span>{h['now']}</h2>
      <div class="panel now">
        <ul>
{now_items}
        </ul>
        <p class="now-updated">{h['now_updated']}</p>
      </div>
    </section></div>

    <div class="band"><section class="wrap" id="projects" aria-labelledby="projects-heading">
      <h2 id="projects-heading" class="reveal">{h['projects']}</h2>
      <div class="projects">
{cards}
      </div>
    </section></div>

    <div class="band alt" id="activityBand" hidden><section class="wrap reveal" id="activity" aria-labelledby="activity-heading">
      <h2 id="activity-heading">{h['activity']}</h2>
      <div class="panel">
        <p class="activity-total"><strong id="activityCount"></strong> <span>{h['activity_total']}</span></p>
        <div class="activity-graph" id="activityGraph" role="img" aria-label="{h['graph_label']}"></div>
        <div class="activity-legend" aria-hidden="true">{h['less']} <i class="l0"></i><i class="l1"></i><i class="l2"></i><i class="l3"></i><i class="l4"></i> {h['more']}</div>
      </div>
    </section></div>

    <div class="band"><section class="wrap reveal" id="til" aria-labelledby="til-heading">
      <div class="section-head">
        <h2 id="til-heading">{h['notes']}</h2>
        <a class="more-link" href="/til/">{h['all_notes']}</a>
      </div>
      {h['notes_note']}
      <ul class="note-list no-dates">
{notes_list(3, lang, dates=False)}
      </ul>
    </section></div>

    <div class="band alt"><section class="wrap reveal" id="about" aria-labelledby="about-heading">
      <h2 id="about-heading">{h['about']}</h2>
      {about_code(lang)}
    </section></div>

    <div class="band"><section class="wrap reveal cta" aria-labelledby="cta-heading">
      <div>
        <h2 id="cta-heading">{h['cta']}</h2>
        <p>{h['cta_sub']}</p>
      </div>
      <div class="links">
        <a class="btn btn-primary" href="{LINKEDIN}" target="_blank" rel="noopener">{h['cta_btn']}</a>
        <a class="btn btn-ghost" href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
      </div>
    </section></div>
  </main>

{footer(lang, home)}
{palette(lang)}
{TAIL}"""
    alts = [("en", "/"), ("ar", "/ar/"), ("x-default", "/")]
    page = head(lang, h["title"], h["desc"], path, extra=JSONLD if lang == "en" else "", alternates=alts) + body
    write(path + "index.html", page)

# ───────────────────────── Notes pages
def sub_nav(lang="en"):
    return [("TIL", "/til/", False), ("Uses", "/uses/", False)]

def article_page(path, title, desc, crumbs, header_html, body_html, published=None, og_image="/og.png"):
    ld = ""
    if published:
        ld = f"""
  <script type="application/ld+json">
  {json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "description": desc,
               "datePublished": published, "url": "https://wacns.com" + path,
               "author": {"@type": "Person", "name": "Abdullah", "alternateName": "wacns", "url": "https://wacns.com/"}}, ensure_ascii=False)}
  </script>"""
    page = head("en", title + " — wacns", desc, path, extra=ld, og_image=og_image) + f"""
<body>
  <div class="hero-fx" aria-hidden="true"><div class="hero-glow"></div></div>
{topbar('en', sub_nav(), '/', lang_href='/ar/').replace('<header class="topbar" id="topbar">', '<header class="topbar solid" id="topbar">')}

  <main id="content">
    <div class="wrap page-head">
      <p class="crumbs">{crumbs}</p>
      {header_html}
    </div>
    <article class="wrap prose">
{body_html}
    </article>
  </main>

{footer('en', '/')}
{palette('en')}
{TAIL}"""
    write(path + "index.html", page)

def til_index():
    article_page("/til/", "Today I Learned", "Short notes on things I’ve picked up while building, one idea per entry.",
        '<a href="/">Home</a> / TIL',
        '<h1>Today I Learned</h1>\n      <p class="lede">Short notes on things I’ve picked up while building. One idea per entry, written down so I don’t have to learn it twice.</p>',
        f'      <ul class="note-list">\n{notes_list()}\n      </ul>', og_image="/til/og.png")

def kw(t): return tk("kw", t)
def st(t): return tk("str", t)
def cm(t): return tk("cm", t)
def pu(t): return tk("pu", t)
def fn(t): return tk("fn", t)
def pr(t): return tk("pr", t)
def tg(t): return tk("kw", t)

def til_entry(n, minutes, body):
    article_page(f"/til/{n['slug']}/", n["title"], n["summary"],
        '<a href="/">Home</a> / <a href="/til/">TIL</a>',
        f'<h1>{html.escape(n["title"])}</h1>\n      <p class="page-meta"><time datetime="{n["date"]}">{n["nice"]}</time> · {minutes} min read</p>',
        body, published=n["date"], og_image=f"/til/{n['slug']}/og.png")

def til_worker():
    n = TIL["worker-subdomain-catch-all"]
    worker = "\n".join([
        f'{kw("const")} SITE_HOSTS {pu("=")} {kw("new")} {tk("ty","Set")}{pu("([")}{st(chr(34)+"example.com"+chr(34))}{pu(",")} {st(chr(34)+"www.example.com"+chr(34))}{pu("]);")}',
        f'{kw("const")} APP_HOSTS  {pu("=")} {kw("new")} {tk("ty","Set")}{pu("([")}{st(chr(34)+"app.example.com"+chr(34))}{pu("]);")}',
        "",
        f'{kw("export default")} {pu("{")}',
        f'  {kw("async")} {fn("fetch")}{pu("(")}request{pu(",")} env{pu(") {")}',
        f'    {kw("const")} host {pu("=")} {kw("new")} {tk("ty","URL")}{pu("(")}request{pu(".")}url{pu(").")}hostname{pu(";")}',
        f'    {kw("if")} {pu("(")}SITE_HOSTS{pu(".")}{fn("has")}{pu("(")}host{pu("))")} {kw("return")} env{pu(".")}ASSETS{pu(".")}{fn("fetch")}{pu("(")}request{pu(");")}',
        f'    {kw("if")} {pu("(")}APP_HOSTS{pu(".")}{fn("has")}{pu("(")}host{pu("))")}  {kw("return")} {fn("fetch")}{pu("(")}request{pu(");")}  {cm("// safety net")}',
        "",
        f'    {kw("const")} page {pu("=")} {kw("await")} env{pu(".")}ASSETS{pu(".")}{fn("fetch")}{pu("(")}{kw("new")} {tk("ty","URL")}{pu("(")}{st(chr(34)+"/404.html"+chr(34))}{pu(",")} request{pu(".")}url{pu("));")}',
        f'    {kw("return")} {kw("new")} {tk("ty","Response")}{pu("(")}page{pu(".")}body{pu(", {")} status{pu(":")} {st("404")}{pu(",")} headers{pu(":")} page{pu(".")}headers {pu("});")}',
        f'  {pu("},")}',
        pu("};"),
    ])
    body = f"""      <p>I wanted any subdomain that doesn’t exist, like <code>hello.example.com</code>, to show my own 404 page instead of a “site can’t be reached” error, without touching the subdomains that already run real apps. Three Cloudflare details made it work.</p>

      <h2>1. A wildcard record never beats a real one</h2>
      <p>A proxied <code>AAAA</code> record for <code>*.example.com</code> pointing to <code>100::</code> (Cloudflare’s placeholder for “handled at the edge”) catches every name that has no record of its own. Explicit records always win, so existing subdomains resolve exactly as before.</p>

      <h2>2. A route with no Worker is a valid route</h2>
      <p>A Worker route <code>*.example.com/*</code> sends all those requests to one Worker. To keep an app out of it, add a more specific route like <code>app.example.com/*</code> and attach <em>no</em> Worker. The most specific route wins, so app traffic never reaches the Worker at all.</p>

      <h2>3. A static-assets Worker can run code first</h2>
      <p>Setting <code>run_worker_first: true</code> in <code>wrangler.jsonc</code> gives the script every request before the static files are served, so it can decide by hostname:</p>
      {code_card("worker.js", worker)}
      <p>One thing to remember: the catch-all is greedy. Every new app subdomain needs its own no-Worker route, or it gets the 404 page too.</p>"""
    til_entry(n, 2, body)

def til_assetsignore():
    n = TIL["assetsignore"]
    ignore = "\n".join([cm("# Never upload these as public assets"), ".git", ".git/**", ".claude", ".claude/**", "CLAUDE.md",
                        "wrangler.jsonc", "worker.js", "tools", "tools/**", ".assetsignore"])
    body = f"""      <p>Cloudflare Workers can serve a static site straight from a repository. What I hadn’t realised: <strong>every file in the assets directory gets published</strong>, including dot-folders like <code>.git</code> and anything else sitting in the repo, such as internal docs or tooling.</p>
      <p>That matters most for plain HTML repos with no build step. If Wrangler generates the config for you, it points the assets directory at <code>.</code>, the whole checkout.</p>

      <h2>The fix: <code>.assetsignore</code></h2>
      <p>Put a file named <code>.assetsignore</code> in the root of the assets directory. It uses the same pattern syntax as <code>.gitignore</code>, and anything it matches is never uploaded:</p>
      {code_card(".assetsignore", ignore)}

      <h2>A ten-second check after any deploy</h2>
      <p>Ask for something that should never be public and make sure it 404s:</p>
      {code_card("terminal", cm("$ ") + "curl -sI https://example.com/.git/HEAD | head -1" + chr(10) + st("HTTP/2 404"))}
      <p>Worth doing whenever a deploy tool picks the defaults for you. Generated configs are convenient, and generous about what they include.</p>"""
    til_entry(n, 2, body)

def til_bdi():
    n = TIL["bdi-rtl"]
    snippet = "\n".join([
        f'{pu("<")}{tg("p")} {pr("dir")}{pu("=")}{st(chr(34)+"rtl"+chr(34))}{pu(">")}',
        f'  أبني أنظمة خلفية باستخدام {pu("<")}{tg("bdi")}{pu(">")}.NET{pu("</")}{tg("bdi")}{pu(">")} و {pu("<")}{tg("bdi")}{pu(">")}C#{pu("</")}{tg("bdi")}{pu(">")}',
        f'{pu("</")}{tg("p")}{pu(">")}',
    ])
    css = "\n".join([
        f'{tk("ty","html")}{pu("[")}{pr("dir")}{pu("=")}{st(chr(34)+"rtl"+chr(34))}{pu("]")} {tk("ty","bdi")} {pu("{")}',
        f'  {pr("direction")}{pu(":")} ltr{pu(";")}',
        f'  {pr("unicode-bidi")}{pu(":")} isolate{pu(";")}',
        pu("}"),
    ])
    body = f"""      <p>While building the Arabic version of this site, a sentence that mentions <code>.NET</code> and <code>C#</code> came out as <strong>NET.</strong> and <strong>#C</strong>. Nothing was wrong with the text itself. It was the Unicode bidirectional algorithm doing exactly what it’s designed to do.</p>

      <h2>Why it happens</h2>
      <p>In a right-to-left paragraph, letters like <code>N</code> are strongly left-to-right, but punctuation such as <code>.</code> and <code>#</code> has no strong direction of its own. When a neutral character sits at the edge of a Latin word, it takes the paragraph’s direction, so it gets drawn on the “wrong” side of the word.</p>

      <h2>The fix: isolate the term</h2>
      <p><code>&lt;bdi&gt;</code> (bidirectional isolate) lays its content out on its own, and the surrounding text treats it as a single unit:</p>
      {code_card("index.html", snippet)}
      <p><code>&lt;bdi&gt;</code> guesses the direction from the first strong character, which is right for <code>.NET</code>. To make it explicit for every term, including ones that start with a digit, I also force left-to-right in CSS:</p>
      {code_card("site.css", css)}

      <h2>Related: keep code blocks left-to-right</h2>
      <p>On an RTL page, code blocks inherit the right-to-left direction too, so brackets and comment markers get mirrored. Setting <code>direction: ltr</code> on code containers keeps them reading like code.</p>"""
    til_entry(n, 2, body)

def uses_page():
    groups = [
      ("Languages &amp; frameworks", [("C# &amp; ASP.NET Core", "Where most of my backend work lives: APIs, background jobs and reporting."),
                                     ("Node.js", "Bots, scrapers and small services, often with discord.js or Puppeteer."),
                                     ("Plain HTML &amp; CSS", "This site. No framework, no build step.")]),
      ("Data", [("MySQL", "My main database, and the one I spend the most time tuning."),
                ("MongoDB", "For bots and projects with loose, document-shaped data."),
                ("Supabase", "Auth and Postgres for FinancialAdvisor.")]),
      ("Infrastructure", [("Cloudflare", "DNS, Workers, Tunnels and Zero Trust. This site runs on a Worker."),
                          ("Docker", "Packaging APIs so they run the same everywhere."),
                          ("GitHub Actions", "CI, plus scheduled jobs like the 8 Ball Pool collector.")]),
      ("Automation", [("Puppeteer", "Driving a real browser when there’s no API."),
                      ("Claude", "Pair-programming, reviews and chores like this site’s redesign.")]),
    ]
    body = ""
    for g, items in groups:
        lis = "\n".join(f"          <li><strong>{n}</strong><span>{d}</span></li>" for n, d in items)
        body += f"""      <section class="uses-group">
        <h2>{g}</h2>
        <ul class="uses-list">
{lis}
        </ul>
      </section>
"""
    article_page("/uses/", "Uses", "The languages, data stores and tools I use to build things.",
        '<a href="/">Home</a> / Uses',
        '<h1>Uses</h1>\n      <p class="lede">The languages, data stores and tools I reach for when I build things.</p>',
        body.rstrip("\n"), og_image="/uses/og.png")

def privacy_page():
    body = """      <p>Short version: this is a personal site. I don\u2019t run ads, sell data or build profiles of anyone. Here\u2019s exactly what happens when you visit.</p>

      <h2>Always on, no cookies</h2>
      <ul>
        <li><strong>Cloudflare Web Analytics</strong> counts page views, the country you\u2019re in, your device type and the page that sent you here. It uses no cookies and doesn\u2019t identify or follow you.</li>
        <li><strong>Cloudflare</strong> hosts the site and, like any server, sees your IP address to deliver pages and block attacks.</li>
        <li><strong>GitHub</strong>: the project stats and activity graph are loaded by your browser from GitHub\u2019s public API and a contributions service, which see your IP address like any website you load.</li>
      </ul>

      <h2>Only if you allow it</h2>
      <p><strong>Google Analytics</strong> shows me which pages are useful and how people find them. It sets cookies (<code>_ga</code>, <code>_ga_*</code>) and Google processes the data under its own privacy policy. It doesn\u2019t load at all unless you choose <em>Allow</em> in the cookie banner.</p>
      <p>You can change your mind any time with <em>Cookie settings</em> at the bottom of every page. Choosing <em>No thanks</em> stops it and removes its cookies.</p>

      <h2>Stored in your browser only</h2>
      <p>Your theme, intro length and cookie choice are saved in your browser\u2019s local storage so the site remembers them. They never leave your device.</p>

      <h2>Contact</h2>
      <p>Questions about any of this: message me on <a href="https://www.linkedin.com/in/abdullah-mohammed-137928219" target="_blank" rel="noopener">LinkedIn</a>.</p>"""
    article_page("/privacy/", "Privacy", "What this site collects, and what it doesn\u2019t.",
        '<a href="/">Home</a> / Privacy',
        '<h1>Privacy</h1>\n      <p class="page-meta">Last updated <time datetime="2026-10-24">Oct 24, 2026</time></p>',
        body)

def page_404():
    """Also served for unknown *.wacns.com hosts, so every link is absolute to wacns.com."""
    body = f"""
<body>
  <div class="hero-fx" aria-hidden="true"><div class="hero-bg"></div><div class="hero-glow"></div></div>
{topbar('en', sub_nav(), '/', lang_href='/ar/')}

  <main id="content" class="nf">
    <div class="wrap nf-inner">
      <p class="nf-code" aria-hidden="true">404</p>
      <h1>Page not found</h1>
      <p class="lede">This page doesn\u2019t exist, or it may have moved.</p>
      <div class="links">
        <a class="btn btn-primary" href="/">Go to the homepage</a>
        <a class="btn btn-ghost" href="/til/">Today I learned</a>
      </div>
      <p class="nf-hint">Tip: press <kbd>Ctrl</kbd> <kbd>K</kbd> or <kbd>/</kbd> to search the site.</p>
    </div>
  </main>

{footer('en', '/')}
{palette('en')}
{TAIL}"""
    page = head("en", "Page not found — wacns", "This page doesn\u2019t exist.", "/404.html", og=False, canonical=False, robots="noindex") + body
    # Make site links absolute (shared files under /assets and /favicon.svg are served on every host)
    for a in ('href="/"', 'href="/til/"', 'href="/uses/"', 'href="/ar/"', 'href="/#projects"', 'href="/privacy/"'):
        page = page.replace(a, a.replace('"/', '"https://wacns.com/'))
    write("/404.html", page)

homepage("en")
homepage("ar")
page_404()
privacy_page()
til_index()
til_assetsignore()
til_worker()
til_bdi()
uses_page()
