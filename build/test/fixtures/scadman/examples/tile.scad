// A tile through a helper
// This example never names tessella: shapes.scad at the repo root does, so the library has to be
// staged beside that file for the live customizer to find it.
use <../shapes.scad>

/* [Tile] */
// Squares along each side
n = 3; // [1:6]

square_tile(n);
