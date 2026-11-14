# just-the-docs-template-openscad

A documentation site for an OpenSCAD repo, built by a GitHub Action: [Just the Docs](https://github.com/just-the-docs/just-the-docs) with OpenSCAD light and dark colour schemes, 3D views of the repo's models and examples, and a live customizer. The theme is adapted from [just-the-docs-template](https://github.com/just-the-docs/just-the-docs-template).

## Use it

`build/` is the Action. It builds the site from the repo as it is, without copying anything into it: the repo keeps one workflow file, and the theme (in `theme/` here), the build and the model embeds stay in this repo and update by version. Copying `docs/` and `.github/` into a project, as earlier versions of this README said, is no longer the way to use it.

What it publishes:

- `README.md` as the home page, with the images it shows.
- Each `examples/*.scad` on an Examples page, as a 3D view with a live customizer, titled by its leading comment.
- Files named by `models:` on a Model page, the same way, for a repo whose main file is the model.
- The repo's own Markdown pages, with `pages: docs`.
- Libraries from outside the repo, with `libraries:`, for the renders and the live customizer.

[Configuration](docs/configuration.md) lists every key of the optional `docs-site.yml`. [Pages and examples](docs/pages-and-examples.md) and [Models and libraries](docs/models-and-libraries.md) cover each in detail.

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
