// Shapes built on tessella, for an example that includes this file and not tessella itself.
use <tessella/tess.scad>

module square_tile(n = 3) {
  centers = squares_centers_rect(10, n, n);
  generic_poly(vertices = squares_vertices(side = 9, centers = centers), paths = [[0, 1, 2, 3, 0]],
               centers = centers, extrude = 2);
}
