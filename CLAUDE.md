# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Static GitHub Pages site at https://wacns.github.io/. Pushing to `main` auto-deploys — there is no build step, CI, or staging environment.

## Stack

Pure HTML/CSS — no package manager, no build tools, no preprocessors. Edit `index.html` directly.

## Workflow

- Before implementing any change, propose a plan and get approval.
- When suggesting changes, explain the tradeoffs.
- Keep responses concise.

## Deployment

```
git add index.html
git commit -m "<message>"
git push origin main
```

Changes are live at https://wacns.github.io/ within ~60 seconds of push.
