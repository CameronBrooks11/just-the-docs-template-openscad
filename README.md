# just-the-docs-template-openscad

This is a documentation template for OpenSCAD template using [just-the-docs](https://github.com/just-the-docs/just-the-docs) adapted from the [just-the-docs-template](https://github.com/just-the-docs/just-the-docs-template). There are OpenSCAD-themed stylings applied in both light and dark options. It is set up such that you can just drop the `docs` and `.github` directories into your existing project and start using it right away. Make sure actions are enabled on your repository before tring to commit and push up the new documentation.

## Use the engine instead of copying

`build/` is a GitHub Action that builds a site like this one from any OpenSCAD repo, without copying anything into it. The repo keeps one workflow file; the theme, the build and the model embeds stay here and update by version.

What it publishes:

- `README.md` becomes the home page. Images it shows are published beside it; links to an example go to that example; links to any other file go to the file on GitHub.
- Each `examples/*.scad` is rendered with OpenSCAD onto an Examples page: a 3D view that loads when clicked, with a live customizer behind it, or a picture if the example is 2D. The first lines of `//` comments become its title and description.
- An optional `docs-site.yml` sets `title`, `description`, `color_scheme` (`openscad-light` or `openscad-dark`) and `live` (`false` to leave out the customizer).

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
