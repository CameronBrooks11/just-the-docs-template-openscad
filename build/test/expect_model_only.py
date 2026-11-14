#!/usr/bin/env python3
"""Check the model-only fixture's built site.

usage: expect_model_only.py SITE_DIR SUMMARY_JSON [--no-models]

The fixture (build/test/fixtures/model-only) has a README, one model named by
docs-site.yml's models key, and no examples/ folder.
"""
import json
import sys
from pathlib import Path


def main(argv):
    site, summary = Path(argv[0]), json.loads(Path(argv[1]).read_text())
    models = "--no-models" not in argv
    index = (site / "index.html").read_text()
    model = (site / "model.html").read_text() if (site / "model.html").is_file() else ""
    checks = [
        ("the model has a page", model != ""),
        ("there is no Examples page", not (site / "examples.html").exists()),
        ("a link to the model goes to its section", 'href="model.html#model-box"' in index),
        ("the model is embedded with a live upgrade",
         'data-src="/engine-model-only/models/model-box/"' in model
         and 'data-live-src="/engine-model-only/models/model-box-live/"' in model),
        ("the summary lists the model and no examples",
         summary["models"] == [{"path": "box.scad", "slug": "model-box", "is3d": True}] and summary["examples"] == []),
    ]
    if models:
        checks.append(("the model's mounts are published, with a poster",
                       (site / "models/model-box/poster.png").is_file()
                       and (site / "models/model-box-live/index.html").is_file()))
    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
    print("all expectations met" if not failed else f"{len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
