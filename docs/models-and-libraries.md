---
title: Models and libraries
nav_order: 4
---

# Models and libraries

## Models

For a repo whose main file is the model, `models:` in `docs-site.yml` names it, or several, comma-separated:

```yaml
models: src/house.scad
```

Each goes on a Model page before the Examples page, titled by its path, with the same 3D view and live customizer
as an example, and links to it go there. The customizer shows the file's own parameters, so they read best with
OpenSCAD's Customizer comments:

```openscad
/* [Box] */
// Length (mm)
length = 40; // [10:100]
```

This site's Model page is built from [`models/demo.scad`](../models/demo.scad).

## Libraries

A library from outside the repo goes in `docs-site.yml` as `libraries:`, comma-separated `name=owner/repo@ref`
entries, each naming a public GitHub repo at a tag or commit:

```yaml
libraries: BOSL2=BelfrySCAD/BOSL2@v2.0.716
```

The engine clones each library at that ref and renders with it on OpenSCAD's library path, so
`include <BOSL2/std.scad>` works as it does on a machine with the library installed. For the live customizer, which
finds an include relative to the file that includes it, the library is copied beside every published file and every
repo file that includes it.

The ref is pinned: a library update reaches the site only when the repo changes the ref.

### With scadman

A repo that pins its libraries with [scadman](https://github.com/CameronBrooks11/scadman) needs no `libraries:` key.
When the repo has a `scadman.lock`, the engine installs scadman and runs `scadman env`. That fetches each library at the
commit the lock records, and the engine renders and stages them the same way as above. Commit both `scadman.toml` and
`scadman.lock`. A lock that no longer matches `scadman.toml` stops the build with scadman's message: run `scadman lock`
and commit the result.

`libraries:` and `scadman.lock` together stop the build too, so that only one of them pins the libraries.
