---
title: Advanced Usage
parent: Usage
nav_order: 2
---

# Advanced Usage

Dive into parameters, modules, and best practices:

- **Parametric modules**
- **Library paths** (`use <...>`, `include <...>`)
- **Combining multiple modules**

```c
// mymodule.scad
module foo(size=10) {
  cylinder(h=size, r=size/2);
}
```

```c
// main.scad
use <mymodule.scad>;
foo(size=20);
```
