---
title: Configuration
nav_order: 2
---

# Configuration

A site needs no configuration: the workflow alone builds one from the README and `examples/`. An optional
`docs-site.yml` at the repo root changes what it publishes. It takes flat `key: value` lines, one per key.

| Key | Default | What it does |
|---|---|---|
| `title` | the repo's name | The site's title. |
| `description` | empty | The site's description, for search engines and link previews. |
| `color_scheme` | `openscad-light` | `openscad-dark` for the dark scheme. |
| `live` | `true` | `false` leaves out the live customizers; the 3D views stay. |
| `models` | none | Comma-separated paths of files to show on a Model page. See [Models and libraries](models-and-libraries.md). |
| `libraries` | none | Comma-separated `name=owner/repo@ref` libraries from outside the repo. See [Models and libraries](models-and-libraries.md). |
| `pages` | none | A folder of the repo's own Markdown pages. See [Pages and examples](pages-and-examples.md). |
| `math` | `false` | `true` loads MathJax on every page. |
| `examples` | an Examples page | `none` or `embed`. See [Pages and examples](pages-and-examples.md). Any other value stops the build. |

This site's own `docs-site.yml`:

```yaml
title: just-the-docs-template-openscad
description: A documentation site for an OpenSCAD repo, built by a GitHub Action.
pages: docs
models: models/demo.scad
```
