#!/usr/bin/env python3
"""Check the library fixture's built site.

usage: expect_library.py SITE_DIR SUMMARY_JSON [--no-models]

The fixture (build/test/fixtures/library) has one example, examples/grid.scad,
that uses tessella, a library outside the repo that docs-site.yml names. The
build only succeeds if the engine fetched it and rendered with it; these check
what it published.
"""
import json
import sys
from pathlib import Path


def main(argv):
    site, summary = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    models = "--no-models" not in argv
    examples = (site / "examples.html").read_text() if (site / "examples.html").is_file() else ""
    checks = [
        ("the summary lists the library", summary.get("libraries") == ["tessella"]),
        ("the example rendered in 3D", summary["examples"] == [{"name": "grid", "slug": "grid", "is3d": True}]),
        ("the example is embedded with a live upgrade",
         'data-src="/engine-library/models/grid/"' in examples
         and 'data-live-src="/engine-library/models/grid-live/"' in examples),
    ]
    if models:
        checks.append(("the example's mounts are published, with a poster",
                       (site / "models/grid/poster.png").is_file() and (site / "models/grid-live/index.html").is_file()))
    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
    print("all expectations met" if not failed else f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
