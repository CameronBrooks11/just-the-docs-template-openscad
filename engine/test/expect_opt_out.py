#!/usr/bin/env python3
"""Check the opt-out fixture's built site.

usage: expect_opt_out.py SITE_DIR SUMMARY_JSON

The fixture (engine/test/fixtures/opt-out) sets `pages: docs` and `examples: none`.
Its docs/ has no index.md, so the README is home, and a hand-written
docs/examples/index.md. Its examples/part.scad draws nothing, so rendering it
would fail the build.
"""
import json
import re
import sys
from pathlib import Path


def main(argv):
    site, summary = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    read = lambda p: (site / p).read_text() if (site / p).is_file() else ""
    index, page = read("index.html"), read("examples/index.html")
    # Each stylesheet ends with a source-map comment naming itself; compare the rest.
    css = lambda name: re.sub(r"/\*# sourceMappingURL=[^*]*\*/\s*$", "",
                              (site / f"assets/css/just-the-docs-{name}.css").read_text())
    nav = re.findall(r'class="nav-list-link[^"]*"[^>]*>([^<]+)<', index)
    part = "https://github.com/CameronBrooks11/engine-opt-out/blob/HEAD/examples/part.scad"
    checks = [
        ("there is no generated Examples page", not (site / "examples.html").exists()),
        ("the summary lists no examples and no mounts", summary["examples"] == [] and summary["targets"] == []),
        ("without a pages index.md, the README is home", "A repo that shows its examples" in index),
        ("the hand-written examples page is published", "A hand-written page" in page),
        ("the navigation has one Examples entry", nav == ["Home", "Examples"]),
        ("the README links to the hand-written page", 'href="examples/index.html"' in index),
        ("links to an example go to GitHub", f'href="{part}"' in index and f'href="{part}"' in page),
        ("color_scheme: openscad-dark fixes the scheme", 'var fixed = "openscad-dark";' in index),
        ("the fixed scheme is the built default", "just-the-docs-default.css" in index
         and css("default") == css("openscad-dark")),
        ("the header still has the toggle", 'class="scheme-toggle"' in index),
    ]
    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
    print("all expectations met" if not failed else f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
