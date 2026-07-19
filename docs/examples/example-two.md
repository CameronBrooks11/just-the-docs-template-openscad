---
title: Example 2
parent: Examples
nav_order: 2
---

# Example 2 — an embedded model

This page embeds an OpenSCAD model, **lightweight by default**: it shows a
pre-rendered poster you click to load a ~0.6 MB rotatable 3D view — no OpenSCAD
install, no in-browser compiler. Once loaded, use **Customize (live)** to switch
to the full in-browser customizer and change parameters.

{% include openscad.html model="demo" live="demo-live" height="520" title="Parametric Demo" %}

The model above is [`models/demo.scad`](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/models/demo.scad):

```scad
/* [Box] */
length = 40; // [10:100]
width = 25; // [10:100]
height = 15; // [5:50]

/* [Rounding] */
radius = 4; // [0:0.5:20]

module rounded_box(l, w, h, r) {
  hull()
    for (x = [r, l - r], y = [r, w - r])
      translate([x, y, 0]) cylinder(h = h, r = r);
}

rounded_box(length, width, height, radius);
```

## How the embed works

1. The model lives at `models/demo.scad` in this repo.
2. On deploy, [`.github/workflows/pages.yml`](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/.github/workflows/pages.yml)
   pre-renders it to an OFF geometry + PNG poster with the OpenSCAD CLI.
3. [`openscad-publish.yml`](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/openscad-publish.yml)
   publishes **two surfaces**: a light `static` one at `/models/demo/` (the
   default) and a live `customizer` at `/models/demo-live/` (the upgrade).
4. The [openscad-web](https://github.com/CameronBrooks11/openscad-web) GitHub
   Action assembles both into the site — **served from this same site**, no
   external host. The `static` mount is self-contained and light (~0.6 MB); the
   compiler runtime lives only in the `customizer` mount and loads only if a
   reader upgrades. (With several live models, those share one runtime on disk.)
5. The page embeds it with a one-line Liquid include:

   {% raw %}`{% include openscad.html model="demo" live="demo-live" height="520" title="Parametric Demo" %}`{% endraw %}

The `// [min:max]` comments in the source drive the customizer sliders, and the
`/* [Group] */` headers become collapsible sections in the live panel.

For a light-only embed, drop `live=`; for the live customizer by default, use
`surface="customizer"`.
