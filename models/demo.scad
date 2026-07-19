// Parametric demo model for the OpenSCAD docs template.
//
// This file is published into the docs site by the openscad-web GitHub Action
// (see .github/workflows/pages.yml + openscad-publish.yml) and embedded in a
// documentation page with {% include openscad.html model="demo" %}.
//
// The annotations below (group headers and value ranges) drive the in-browser
// customizer panel.

/* [Box] */
// Length (mm)
length = 40; // [10:100]
// Width (mm)
width = 25; // [10:100]
// Height (mm)
height = 15; // [5:50]

/* [Rounding] */
// Corner radius (mm)
radius = 4; // [0:0.5:20]
// Facets (smoothness)
facets = 48; // [12:4:120]

$fn = facets;

module rounded_box(l, w, h, r) {
  hull()
    for (x = [r, l - r], y = [r, w - r])
      translate([x, y, 0]) cylinder(h = h, r = r);
}

rounded_box(length, width, height, radius);
