// tray.scad: the fixture's model, a tray built on the library's block.
use <../lib.scad>

/* [Tray] */
// Outside length (mm)
length = 40; // [20:5:100]
// Outside width (mm)
width = 25; // [15:5:60]
// Wall and floor (mm)
wall = 2; // [1:0.5:4]

difference() {
  rounded_block([length, width, 10], r = 3);
  translate([0, 0, wall]) rounded_block([length - 2 * wall, width - 2 * wall, 10], r = 2);
}
