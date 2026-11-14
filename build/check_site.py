#!/usr/bin/env python3
"""Check a built site before it is published.

usage: check_site.py SITE_DIR SUMMARY_JSON [--no-models]

Fails (exit 1, one line per problem) when:
  - a local href or src in any page does not resolve to a file in the site
  - a link's #fragment names no id in the page it points to
  - a link still points at a .md file
  - a model or example published in 3D has no model mount (an index.html under
    models/<name>/), or its static mount has no poster.png for the embed
--no-models skips the mounts, and links into models/, for a build that has not
run openscad-web (a local build).
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


def main(argv):
    site, summary_path = Path(argv[0]), Path(argv[1])
    check_models = "--no-models" not in argv
    summary = json.loads(summary_path.read_text())
    base = summary["base_path"].rstrip("/")
    problems, pages, refs = [], 0, 0
    ids = {}

    def has_id(page_path, frag):
        if page_path not in ids:
            ids[page_path] = set(re.findall(r'\bid="([^"]+)"', page_path.read_text(errors="replace")))
        return frag in ids[page_path]

    for page in sorted(site.rglob("*.html")):
        rel_page = page.relative_to(site)
        # Model surfaces are openscad-web's own app; only the docs pages are checked.
        if rel_page.parts[0] == "models":
            continue
        pages += 1
        html = page.read_text(errors="replace")
        for attr, link in re.findall(r'\b(href|src)="([^"]*)"', html):
            u = urlparse(link)
            if link.startswith("#") and len(link) > 1:
                if not has_id(page, unquote(link[1:])):
                    problems.append(f"{rel_page}: {attr}={link} names no id on this page")
                continue
            if u.scheme or link.startswith("//") or link.startswith("data:") or not link or link == "#":
                continue
            refs += 1
            path = unquote(u.path)
            if path.endswith(".md"):
                problems.append(f"{rel_page}: {attr}={link} still points at a .md file")
                continue
            if not check_models and (path.startswith(base + "/models/") or path.startswith("models/")):
                continue
            if path.startswith("/"):
                if base and not (path == base or path.startswith(base + "/")):
                    problems.append(f"{rel_page}: {attr}={link} is outside the base path {base or '/'}")
                    continue
                target = site / path[len(base):].lstrip("/")
            else:
                target = (page.parent / path)
            if path.endswith("/") or target.is_dir():
                target = target / "index.html"
            if not target.exists():
                problems.append(f"{rel_page}: {attr}={link} does not resolve")
            elif u.fragment and target.suffix == ".html" and not has_id(target, unquote(u.fragment)):
                problems.append(f"{rel_page}: {attr}={link} names no id in {target.relative_to(site)}")

    if check_models:
        for mount in summary["targets"]:
            if not (site / mount / "index.html").exists():
                problems.append(f"model mount {mount}/ has no index.html")
        for ex in summary.get("models", []) + summary["examples"]:
            if ex["is3d"] and not (site / "models" / ex["slug"] / "poster.png").exists():
                problems.append(f"models/{ex['slug']}/ has no poster.png for its embed")

    for p in problems:
        print(p)
    print(f"checked {pages} pages and {refs} local links: "
          + ("ok" if not problems else f"{len(problems)} problems"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
