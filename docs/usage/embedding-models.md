---
title: Embedding Models
parent: Usage
nav_order: 3
---

# Embedding Models

This template can show your OpenSCAD models **in the documentation** — served
from your own site, no external host. See [Example 2](../examples/example-two)
for a live one.

By default an embed is **lightweight**: a pre-rendered image you click to load a
~0.6 MB rotatable 3D view (no in-browser compiler). You can also offer a live
customizer that compiles the model in the browser.

## Add a model

1. Put the `.scad` in `models/` at the repo root (e.g. `models/widget.scad`).

2. Declare it in [`openscad-publish.yml`](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/openscad-publish.yml).
   A `static` surface is pre-rendered; a `customizer` surface is live:

   ```yaml
   targets:
     - surface: static # lightweight, pre-rendered
       geometry: ./rendered/widget.off
       poster: ./rendered/widget.png
       mountPath: /models/widget/
     - surface: customizer # live, in-browser compile
       source: ./models/widget.scad
       mountPath: /models/widget-live/
   ```

3. For a `static` surface, pre-render the geometry in
   [`.github/workflows/pages.yml`](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/.github/workflows/pages.yml)
   with the OpenSCAD CLI (a PNG poster needs a display, hence `xvfb-run`):

   ```bash
   openscad models/widget.scad -o rendered/widget.off
   xvfb-run -a openscad models/widget.scad -o rendered/widget.png \
     --imgsize=1000,750 --viewall --autocenter --render
   ```

4. Embed it in any page:

   {% raw %}```liquid
   {% include openscad.html model="widget" live="widget-live" title="Widget" %}
   ```{% endraw %}

## Include parameters

| Parameter | Meaning                                                          |
| --------- | --------------------------------------------------------------- |
| `model`   | required — the mount name (`mountPath: /models/<model>/`)        |
| `surface` | `static` (default) · `viewer` · `customizer` — how it's published |
| `live`    | optional mount of a live surface, for a "Customize" upgrade      |
| `height`  | view height in px (default `480`)                                |
| `title`   | accessible label (default: the model name)                       |

The models are assembled at deploy time by the
[openscad-web](https://github.com/CameronBrooks11/openscad-web) GitHub Action
(pinned `@v0`), which needs **v0.5+** for the `static` surface.
