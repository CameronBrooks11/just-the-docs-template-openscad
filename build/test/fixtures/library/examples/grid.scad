// A grid of squares from the tessella library.
// tessella is not in this repo: docs-site.yml names it, and the engine stages it.
use <tessella/tess.scad>

/* [Grid] */
// Squares along x
n = 4; // [1:10]
// Squares along y
m = 3; // [1:10]

centers = squares_centers_rect(10, n, m);
generic_poly(vertices = squares_vertices(side = 9, centers = centers), paths = [[0, 1, 2, 3, 0]],
             centers = centers, extrude = 2);
