---
title: Pages and examples
nav_order: 3
---

# Pages and examples

## The home page

`README.md` is the home page. Images it shows are published beside it. A link to an example goes to that example
on the Examples page, a link to the `examples/` folder goes to the Examples page, and a link to any other file goes
to the file on GitHub.

## Examples

Each `examples/*.scad` is rendered with OpenSCAD onto an Examples page: a 3D view that loads when clicked, with a
live customizer behind it, or a picture if the example is 2D.

The file's leading `//` comment gives its title and description. The title is the first sentence, however many
lines it wraps over, or a first line with no closing punctuation followed by a line that starts with a capital:

```openscad
// A rounded block
// The library's one module, at its default size.

include <../block.scad>
```

The comment ends at the first line that isn't a comment, so a blank line after the description keeps the rest of
the file's notes out of it.

When `examples/` has no `.scad` files at its top level, the engine reads its subfolders instead, and each folder
becomes a heading on the Examples page.

Two settings in `docs-site.yml` change this:

- `examples: none` leaves out the Examples page and renders nothing in `examples/`. It suits a repo whose examples
  a page of its own shows better, or whose `examples/` holds files that other files include.
- `examples: embed` renders the examples and publishes their 3D views and customizers, but makes no Examples page:
  the repo's own pages embed them.

With either setting, links to an example go to GitHub.

## The repo's own pages

`pages: docs` publishes the Markdown pages in `docs/` beside the generated ones:

- Each `.md` page is published at its path inside the folder, as `.html`. It goes in the navigation by its own
  front matter (`title`, `nav_order`, `parent`), ahead of the Model and Examples pages.
- If the folder has an `index.md`, that is the home page, and the README isn't published.
- Pages link to each other with relative `.md` links, so the links work on GitHub too. The engine rewrites them, and
  links to examples and models, for the site.
- Images and other files in the folder are published beside the pages.
- Folders starting with `_` or `.`, and a `README.md` in the folder, are left out.

This page is one of those pages.

## Embedding a model in a page

A page embeds an example or a model by the mount the engine gives it:

```liquid
{% raw %}{% include openscad.html model="hexagons-radial" live="hexagons-radial-live" title="Radial hexagons" %}{% endraw %}
```

- **An example's mount** is its path inside `examples/` without `.scad`, lower-cased, with every run of other
  characters turned into `-`. `examples/hexagons/radial.scad` is `hexagons-radial`. When that starts with a digit,
  `example-` goes in front: `01_elbow.scad` is `example-01-elbow`.
- **A model's mount** is `model-` and its path the same way: `models/demo.scad` is `model-models-demo`.

The build fails if a page names a mount that wasn't published.

## Maths

`math: true` in `docs-site.yml` loads MathJax on every page, with `$…$` as inline maths and `$$…$$` as display maths,
as GitHub renders them. A single page can set `math: true` in its front matter instead.
