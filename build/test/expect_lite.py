#!/usr/bin/env python3
"""Check the lite fixture's built site for what the engine promises it.

usage: expect_lite.py SITE_DIR SUMMARY_JSON [--no-models]

The fixture (build/test/fixtures/lite) has a README with an image used twice,
links to a library, a non-published note, the licence, an example and an
anchor, a model and literal {{ braces }}; a model, src/tray.scad (3D, using the
library), named by docs-site.yml's models key; and two examples, block.scad
(3D, using the library) and outline.scad (2D).
"""
import json
import sys
from pathlib import Path

REPO = "https://github.com/CameronBrooks11/engine-fixture"  # the repository the test build passes


def main(argv):
    site, summary = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    models = "--no-models" not in argv
    index = (site / "index.html").read_text()
    examples = (site / "examples.html").read_text()
    model = (site / "model.html").read_text() if (site / "model.html").is_file() else ""
    checks = [
        ("the README is the home page", "<h1" in index and "Engine fixture" in index),
        ("the README image is published once", (site / "images/block.png").is_file() and summary["images"] == ["images/block.png"]),
        ("a link to a library file goes to GitHub", f'href="{REPO}/blob/HEAD/lib.scad"' in index),
        ("a link to an unpublished .md goes to GitHub", f'href="{REPO}/blob/HEAD/NOTES.md"' in index),
        ("a link to an example goes to its section", 'href="examples.html#block"' in index),
        ("literal braces survive Liquid", "{{ like this }}" in index),
        ("the site links to its repo", f'href="{REPO}"' in index),
        ("the 3D example is embedded with a live upgrade",
         'data-src="/engine-fixture/models/block/"' in examples and 'data-live-src="/engine-fixture/models/block-live/"' in examples),
        ("the 2D example is a picture", (site / "assets/examples/outline.png").is_file() and "assets/examples/outline.png" in examples),
        ("each example shows its source", examples.count("Source: examples/") == 2),
        ("3D and 2D are told apart", {e["name"]: e["is3d"] for e in summary["examples"]} == {"block": True, "outline": False}),
        ("the model has a page, listed before Examples",
         model != "" and 0 <= index.find('href="/engine-fixture/model.html"') < index.find('href="/engine-fixture/examples.html"')),
        ("a link to the model goes to its section", 'href="model.html#model-src-tray"' in index),
        ("the model is titled by its path", 'id="model-src-tray"' in model and ">src/tray.scad</code>" in model),
        ("the model is embedded with a live upgrade",
         'data-src="/engine-fixture/models/model-src-tray/"' in model and 'data-live-src="/engine-fixture/models/model-src-tray-live/"' in model),
        ("the model shows its source", "Source: src/tray.scad" in model),
        ("the summary lists the model", summary["models"] == [{"path": "src/tray.scad", "slug": "model-src-tray", "is3d": True}]),
    ]
    if models:
        checks += [
            ("the static mount has a viewer and a poster",
             (site / "models/block/index.html").is_file() and (site / "models/block/poster.png").is_file()),
            ("the live mount is published",
             (site / "models/block-live/index.html").is_file()),
            ("the model's mounts are published, with a poster",
             (site / "models/model-src-tray/poster.png").is_file() and (site / "models/model-src-tray-live/index.html").is_file()),
        ]
    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
    print("all expectations met" if not failed else f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
