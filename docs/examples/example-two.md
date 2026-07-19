---
title: Example 2
parent: Examples
nav_order: 2
---

# Example 2 — an embedded interactive model

This page embeds a live, in-browser OpenSCAD model. Drag to orbit, and use the
**customizer panel** to change its parameters and re-render — no OpenSCAD
install required.

{% include openscad.html model="demo" height="520" title="Parametric Demo" %}

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
2. [`openscad-publish.yml`](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/openscad-publish.yml)
   maps it to a mount path (`/models/demo/`) and a surface (`viewer`).
3. On deploy, the [openscad-web](https://github.com/CameronBrooks11/openscad-web)
   GitHub Action assembles that model into the site — **served from this same
   site**, with no dependency on any external host.
4. The page embeds it with a one-line Liquid include:

   {% raw %}`{% include openscad.html model="demo" height="520" title="Parametric Demo" %}`{% endraw %}

The `// [min:max]` comments in the source drive the customizer sliders, and the
`/* [Group] */` headers become collapsible sections in the panel.
