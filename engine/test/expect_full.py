#!/usr/bin/env python3
"""Check the full fixture's built site.

usage: expect_full.py SITE_DIR SUMMARY_JSON [--no-models]

The fixture (engine/test/fixtures/full) sets `pages: docs` and `math: true`. Its
docs/ has an index.md home page, a guide folder with an inline embed, an image,
a README that isn't a page and a leftover _config.yml. Its examples sit in two
subfolders.
"""
import json
import re
import sys
from pathlib import Path


def nav(html):
    return re.findall(r'class="nav-list-link[^"]*"[^>]*>([^<]+)<', html)


def main(argv):
    site, summary = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    models = "--no-models" not in argv
    read = lambda p: (site / p).read_text() if (site / p).is_file() else ""
    index, guide, shapes, examples = read("index.html"), read("guide/index.html"), read("guide/shapes.html"), read("examples.html")
    checks = [
        ("the pages' index.md is the home page, not the README",
         "Full fixture home" in index and "used to test the docs engine" not in index),
        ("the pages are published at their paths", guide != "" and shapes != ""),
        ("the unpublished README's image isn't copied",
         not (site / "cover.png").exists() and summary["images"] == []),
        ("the folder's README isn't a page", not (site / "README.html").exists()),
        ("an old theme config in the folder doesn't replace the engine's",
         "<title>Home | Full fixture</title>" in index and "Stale title" not in index),
        ("the navigation is the pages in order, then Examples",
         nav(index)[:4] == ["Home", "Guide", "Shapes", "Examples"]),
        (".md links between pages become .html links relative to the page",
         'href="guide/index.html"' in index and 'href="../index.html"' in guide
         and 'href="shapes.html"' in guide and 'href="index.html#guide"' in shapes),
        ("a link to the README goes to the home page", 'href="index.html"' in index),
        ("a link to a nested example goes to its section", 'href="../examples.html#shapes-cube"' in guide),
        ("a link to the examples folder goes to the Examples page", 'href="../examples.html"' in guide),
        ("an image beside the pages keeps its path", 'src="img/block.png"' in index
         and (site / "img/block.png").is_file()),
        ("math: true loads MathJax", "mathjax@3.2.2" in guide),
        ("the inline embed names the engine's mounts",
         'data-src="/engine-full/models/shapes-cube/"' in shapes
         and 'data-live-src="/engine-full/models/shapes-cube-live/"' in shapes),
        ("examples are grouped by folder, slugs include the folder",
         re.findall(r'<h([23])[^>]*id="([^"]*)"', examples)
         == [("2", "3d"), ("3", "example-3d-ring"), ("2", "flat"), ("3", "flat-disc"),
             ("2", "shapes"), ("3", "shapes-cube")]),
        ("the summary lists the pages and the nested examples",
         sorted(summary["pages"]) == ["guide/index.html", "guide/shapes.html", "index.html"]
         and [e["slug"] for e in summary["examples"]] == ["example-3d-ring", "flat-disc", "shapes-cube"]),
    ]
    if models:
        checks.append(("the inline embed's mounts are published",
                       (site / "models/shapes-cube/poster.png").is_file()
                       and (site / "models/shapes-cube-live/index.html").is_file()))
    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
    print("all expectations met" if not failed else f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
