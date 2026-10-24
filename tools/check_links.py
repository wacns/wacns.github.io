#!/usr/bin/env python3
"""Fails if any page links to a file on wacns.com that doesn't exist in the repo.

Usage (from the repo root):  python3 tools/check_links.py
Checks href/src values that start with "/" or "https://wacns.com/". External links are ignored.
"""
import os, re, sys
from html.parser import HTMLParser

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP_DIRS = {".git", "node_modules", ".wrangler", "tools", ".github", ".claude"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.found.append(value)


def local_path(url):
    url = re.sub(r"^https://wacns\.com", "", url)
    if not url.startswith("/") or url.startswith("//"):
        return None
    path = url.split("#")[0].split("?")[0]
    if path.endswith("/"):
        path += "index.html"
    return os.path.join(ROOT, path.lstrip("/"))


def main():
    broken, pages = [], 0
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".html") or name.startswith(".og-tmp"):
                continue
            page = os.path.join(dirpath, name)
            pages += 1
            parser = Links()
            with open(page, encoding="utf-8") as f:
                parser.feed(f.read())
            for url in parser.found:
                if url.startswith("/.well-known/"):
                    continue  # served by Cloudflare, not from the repo
                target = local_path(url)
                if target and not os.path.exists(target):
                    broken.append(f"{os.path.relpath(page, ROOT)} → {url}")
    if broken:
        print("Broken internal links:")
        print("\n".join("  " + b for b in broken))
        sys.exit(1)
    print(f"OK: no broken internal links across {pages} pages")


if __name__ == "__main__":
    main()
