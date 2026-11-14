# just-the-docs-template-openscad

A documentation site for an OpenSCAD repo, built by a GitHub Action: [Just the Docs](https://github.com/just-the-docs/just-the-docs) with OpenSCAD light and dark colour schemes, 3D views of the repo's models and examples, and a live customizer. The theme is adapted from [just-the-docs-template](https://github.com/just-the-docs/just-the-docs-template).

## Use it

`build/` is the Action. It builds the site from the repo as it is, without copying anything into it: the repo keeps one workflow file, and the theme (in `docs/` here), the build and the model embeds stay in this repo and update by version. Copying `docs/` and `.github/` into a project, as earlier versions of this README said, is no longer the way to use it.

What it publishes:

- `README.md` becomes the home page. Images it shows are published beside it; links to an example go to that example, and a link to the `examples/` folder to the Examples page; links to any other file go to the file on GitHub.
- Each `examples/*.scad` is rendered with OpenSCAD onto an Examples page: a 3D view that loads when clicked, with a live customizer behind it, or a picture if the example is 2D. Its leading `//` comment gives its title and description: the title is the first sentence, however many lines it wraps over, or a first line with no closing punctuation followed by a capitalised description line.
- For a repo whose main file is the model, `models:` in `docs-site.yml` names it, or several, comma-separated (`models: src/house.scad`). Each goes on a Model page before the examples, titled by its path, with the same 3D view and customizer, and README links to it go there. The customizer shows the file's own parameters, so they need OpenSCAD's Customizer comments to read well.
- Libraries from outside the repo go in `docs-site.yml` as `libraries:`, comma-separated `name=owner/repo@ref` entries naming a public GitHub repo at a tag or commit (`libraries: BOSL2=BelfrySCAD/BOSL2@v2.0.716`). The engine clones each at that ref, renders with it on OpenSCAD's library path, and copies it beside each published file so the live customizer finds `include <BOSL2/std.scad>` the same way. The ref is pinned: a library update reaches the site only when the repo changes it.
- A repo with its own documentation pages names their folder with `pages: docs`. Every `.md` page in it is published at its path inside the folder, as `.html`, in the navigation by its own front matter (`title`, `nav_order`, `parent`), ahead of the Model and Examples pages. If the folder has an `index.md`, that is the home page and the README isn't published. Links between pages are written as relative `.md` links, so they work on GitHub too; the engine rewrites them, and links to examples and models, for the site. Images and other files in the folder are published beside the pages. Folders starting with `_` or `.` and a `README.md` in the folder are left out, so an old copy of the theme there has no effect, though it is better deleted.
- A page embeds an example or model with `{% include openscad.html model="<mount>" live="<mount>-live" title="…" %}`, where the mount is the one the engine gives it: the example's path inside `examples/` without `.scad`, lower-cased, with every run of other characters turned to `-` (`examples/hexagons/radial_grid.scad` is `hexagons-radial-grid`), or `model-` and the model's path for a model. The build fails if a page names a mount that wasn't published.
- `examples: none` leaves out the Examples page, for a repo whose examples a page of its own shows better, or whose `examples/` holds files that other files include. Links to its examples then go to GitHub.
- `examples: embed` renders the examples and publishes their 3D views and customizers, but makes no Examples page: the repo's own pages embed them by mount. Links to its examples go to GitHub.
- When `examples/` has no `.scad` files at its top level, the engine reads its subfolders instead, and each folder becomes a heading on the Examples page.
- `math: true` loads MathJax on every page, with `$…$` as inline math and `$$…$$` as display math, as GitHub renders them. A single page can set `math: true` in its front matter instead.
- An optional `docs-site.yml` sets `title`, `description`, `color_scheme` (`openscad-light` or `openscad-dark`), `live` (`false` to leave out the customizer), `models`, `libraries`, `pages`, `math` and `examples`.

Every build checks its own links, anchors and model mounts, and fails rather than publishing a broken page.

Add `.github/workflows/docs.yml`, and set Pages to deploy from GitHub Actions (Settings, Pages, Source):

```yaml
name: Docs site

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: docs-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v7
      - id: site
        uses: CameronBrooks11/just-the-docs-template-openscad/build@v1
      - if: github.event_name != 'pull_request'
        uses: actions/upload-pages-artifact@v5
        with:
          path: ${{ steps.site.outputs.site-dir }}

  deploy:
    if: github.event_name != 'pull_request'
    needs: build
    runs-on: ubuntu-24.04
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
```

A pull request builds and checks the site without publishing it.
