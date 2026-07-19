---
title: Functions
parent: Reference
nav_order: 1
---

# Functions

Document each public function: its purpose, parameters, and return value. A
consistent doc-comment style keeps this readable (and lets a tool like Doxygen
generate a reference later).

```scad
// Evenly distribute `n` points around a circle of radius `r`.
//   r : circle radius
//   n : point count
// -> list of [x, y] points
function ring(r, n) = [for (i = [0:n - 1]) let (a = 360 * i / n) [r * cos(a), r * sin(a)]];
```