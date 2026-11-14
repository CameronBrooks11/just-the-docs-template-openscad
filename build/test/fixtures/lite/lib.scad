// A rounded block, the fixture's one library module.
module rounded_block(size = [20, 20, 10], r = 2) {
  minkowski() {
    cube(size - [2 * r, 2 * r, 0], center = true);
    cylinder(r = r, h = 0.001, $fn = 24);
  }
}
