# Stremio Source — Implementation Plan

## Phase 1 — Scaffold & config

- [x] Create `config.js` at repo root (single source of truth; `tvosEnabled: false` by default)
- [x] Create directories: `stremio-source/`, `stremio-source/ios/`, `stremio-source/tvos/`

## Phase 2 — Source JSON files

- [x] `stremio-source/ios/altstore.json`
- [x] `stremio-source/ios/altstore-classic.json`
- [x] `stremio-source/ios/sidestore.json`
- [x] `stremio-source/ios/feather.json`
- [x] `stremio-source/ios/esign.json`
- [x] `stremio-source/ios/ksign.json`
- [x] `stremio-source/ios/gbox.json`
- [x] `stremio-source/ios/scarlet.json` *(Scarlet schema — different from the rest)*
- [ ] `stremio-source/tvos/altstore.json` *(skip until `tvosEnabled: true`)*
- [ ] `stremio-source/tvos/altstore-classic.json` *(skip until `tvosEnabled: true`)*
- [ ] `stremio-source/tvos/sidestore.json` *(skip until `tvosEnabled: true`)*

## Phase 3 — Folder-blocking redirects

- [x] `stremio-source/index.html` → redirects to `/403.html`
- [x] `stremio-source/ios/index.html` → redirects to `/403.html`
- [x] `stremio-source/tvos/index.html` → redirects to `/403.html`

## Phase 4 — Error pages

- [x] `403.html` — dark theme, red accent `#e22b2b`, "Access denied."
- [x] `404.html` — dark theme, purple accent `#8A2BE2`, "Page not found."

## Phase 5 — Landing page

- [x] Replace `index.html` with the Stremio source hub landing page
  - Loads `config.js` via `<script src="config.js">`
  - iOS section: renders all platforms from `CONFIG.platforms`
  - tvOS section: renders only when `CONFIG.tvosEnabled === true`, filtered to `supportsTV: true`
  - Deep-link button (`Add to [Platform]`) when `deepLink !== null`
  - Copy-to-clipboard button + paste hint when `deepLink === null`
  - "Copied!" toast for 2 seconds after copy
  - Footer: `wacns.github.io` + GitHub icon → `https://github.com/wacns`

## Phase 6 — Verify

- [x] Print full file tree — structure confirmed
- [x] Run `html-validate` on `index.html`, `403.html`, `404.html` — 0 errors
- [x] Config platform list matches JSON files on disk — 8/8 ✓
- [ ] Open site in browser (Playwright sandbox can't reach localhost — test after deploy)

## Remaining (when ready)

- [ ] Fill in `PLACEHOLDER_ICON_URL` in `config.js`
- [ ] Fill in `PLACEHOLDER_IOS_IPA_URL` in `config.js`
- [ ] Set `tvosEnabled: true` and add `PLACEHOLDER_TVOS_IPA_URL` when tvOS IPA is ready
  - Then create `stremio-source/tvos/altstore.json`, `altstore-classic.json`, `sidestore.json`
