// box.scad: an open box, the fixture's only model.

/* [Box] */
// Outside size (mm)
size = 30; // [10:5:100]
// Wall and floor (mm)
wall = 2; // [1:0.5:5]

difference() {
  cube(size, center = true);
  translate([0, 0, wall]) cube(size - 2 * wall, center = true);
}
