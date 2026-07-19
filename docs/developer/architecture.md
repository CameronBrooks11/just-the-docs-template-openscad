---
title: Architecture
parent: Developer Guide
nav_order: 1
---

# Architecture

Lay out your repo so readers can find things. A typical OpenSCAD project using
this template:

```text
├─ models/               ← .scad sources (embedded in the docs)
├─ examples/             ← runnable example scripts
├─ docs/                 ← this documentation site
├─ openscad-publish.yml  ← which models to embed, and how
└─ .github/              ← the GitHub Pages build workflow
```

Then describe how your library's modules fit together.
