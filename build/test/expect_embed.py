#!/usr/bin/env python3
"""Check the embed fixture's built site.

usage: expect_embed.py SITE_DIR SUMMARY_JSON [--no-models]

The fixture (build/test/fixtures/embed) sets `pages: docs` and `examples: embed`.
Its docs/examples.md embeds examples/cube.scad by its mount, so the engine has to
render the example and publish its mounts without writing an Examples page.
"""
import json
import re
import sys
from pathlib import Path


def main(argv):
    site, summary = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    models = "--no-models" not in argv
    read = lambda p: (site / p).read_text() if (site / p).is_file() else ""
    index, page = read("index.html"), read("examples.html")
    nav = re.findall(r'class="nav-list-link[^"]*"[^>]*>([^<]+)<', index)
    cube = "https://github.com/CameronBrooks11/engine-embed/blob/HEAD/examples/cube.scad"
    checks = [
        ("the Examples page is the hand-written one", "embedded by its mount" in page and "<summary>Source:" not in page),
        ("the navigation has one Examples entry", nav == ["Home", "Examples"]),
        ("the example is rendered and its mounts listed",
         summary["examples"] == [{"name": "cube", "slug": "cube", "is3d": True}]
         and summary["targets"] == ["models/cube", "models/cube-live"]),
        ("the hand-written page embeds the engine's mounts",
         'data-src="/engine-embed/models/cube/"' in page and 'data-live-src="/engine-embed/models/cube-live/"' in page),
        ("a link to the example goes to GitHub", f'href="{cube}"' in page),
    ]
    if models:
        checks.append(("the mounts are published, with a poster",
                       (site / "models/cube/poster.png").is_file() and (site / "models/cube-live/index.html").is_file()))
    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
    print("all expectations met" if not failed else f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
