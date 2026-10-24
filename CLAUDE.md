# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository.

## Project

Personal site of Abdullah (wacns). Live at **https://wacns.com/** (primary) and https://wacns.github.io/ (GitHub Pages mirror).
Pushing to `main` deploys both automatically — there is no CI, staging or preview step.

- **wacns.com** — Cloudflare Worker `wacns-github-io`, built by Cloudflare Workers Builds on every push to `main`
  (deploy command `npx wrangler deploy`, config in `wrangler.jsonc`). Takes ~1 minute.
- **wacns.github.io** — GitHub Pages serves the repo as-is. It ignores `_headers`, `worker.js` and `wrangler.jsonc`.

## Stack

Plain HTML/CSS/JS. No package manager, no framework, no build step on deploy.

| Path | What it is |
|---|---|
| `index.html`, `ar/index.html` | Homepage in English and Arabic (RTL) |
| `til/` | "Today I learned" index and one folder per entry |
| `uses/` | Tools/stack page |
| `assets/site.css`, `assets/site.js` | Shared styles (dark + light themes) and behaviour (theme toggle, Ctrl+K palette, intro toggle, live GitHub stats, activity heatmap, colophon) |
| `tools/build_pages.py` | Generator for the shared-layout pages above (see below) |
| `404.html` | Generated. Served with a 404 status for missing paths **and unknown subdomains**, so all its site links are absolute (`https://wacns.com/...`) |
| `tools/og_cards.py` | Generates the 1200×630 link-preview images (`til/og.png`, `til/<slug>/og.png`, `uses/og.png`). Needs Python Playwright |
| `stremio/`, `stremio-source/`, `config.js` | Old Stremio sideload hub. **Unlinked** from the site but still live so existing sources keep working |
| `worker.js` | Worker script (hostname routing, see below) |
| `wrangler.jsonc` | Worker config |
| `_headers` | Security headers (HSTS incl. subdomains, CSP, etc.) applied by the Worker |
| `.assetsignore` | Files the Worker must never serve (`.git`, tooling, config). Keep it updated when adding non-public files |
| `robots.txt`, `sitemap.xml` | SEO. Update `sitemap.xml` when adding pages |

### Editing pages

`index.html`, `ar/index.html`, `404.html`, `til/**` and `uses/index.html` are **generated** by `tools/build_pages.py`.
Edit the content in that script, then run from the repo root:

```
python3 tools/build_pages.py .
```

…and commit the regenerated HTML. Editing the generated HTML directly works too, but the next regeneration overwrites it.
When adding a TIL entry: add it to `NOTES` in the script (plus a `til_*` page function), run `python3 tools/og_cards.py .` to create its preview image, **and** to `NOTES` in `assets/site.js` (palette list), and to `sitemap.xml`. Keep entries framed as something learned, not as incident reports.

### Content rules (from the site owner)

- **Do not show work experience or the employer** anywhere on the site. Projects, skills and professional links only.
- **Project cards are display-only** — no links from cards to repos or project pages.
- The "Now" section should be refreshed roughly monthly.

### Validation

`.htmlvalidate.json` holds the html-validate config. Before committing, run:

```
npx html-validate index.html ar/index.html til/index.html til/*/index.html uses/index.html 404.html stremio/index.html
```

The CSP in `_headers` only allows scripts from self + Cloudflare Insights, styles/fonts from Google Fonts,
and `connect-src` to `api.github.com` and `github-contributions-api.jogruber.de`. Update it if you add a new origin.

## Worker and subdomains

`worker.js` runs before static assets (`run_worker_first: true`):

- `wacns.com` / `www.wacns.com` → static site.
- Any other `*.wacns.com` → `404.html` with a 404 status (but `/assets/*` and `/favicon.svg` are served on every host so that page can load its styles and script).
- Known app hosts (`APP_HOSTS` list) → passed through untouched (safety net).

Cloudflare side (configured in the dashboard, not in this repo):

- Proxied wildcard DNS `*.wacns.com` (AAAA `100::`) and Worker route `*.wacns.com/*` → `wacns-github-io`.
- **Exclusion routes with no Worker** for every existing app subdomain (rend, rend-mcp, rend-send, thetower, tower, rdp).
- **When a new app subdomain is added, add a matching no-Worker route (`<host>/*`) and add it to `APP_HOSTS`**, or the catch-all will serve the 404 page instead of the app.
- "Always Use HTTPS" is on for the zone.

## Workflow

- Propose a plan before larger changes; explain trade-offs. Keep responses concise.
- Commits: author `Claude <noreply@anthropic.com>` (signed), **no** `Co-Authored-By` or session-link trailers.

## Deployment

```
git add -A
git commit -m "<message>"
git push origin main
```

Then confirm the Workers Build succeeded (Cloudflare dashboard → Workers & Pages → wacns-github-io → Deployments).
