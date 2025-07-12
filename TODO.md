# TODO

- **Fix Sass deprecation warnings**
  - Replace all `darken()`/`lighten()` calls with the new Dart-Sass APIs (`color.adjust`/`color.scale`), or bump to a Just-the-Docs release that includes the upstream patch (see #1541, #1548).
    - https://github.com/just-the-docs/just-the-docs/issues/1541
    - https://github.com/just-the-docs/just-the-docs/pull/1548
- **Include external source files**
  - Add a pre-build CI step to copy `src/` folder into `docs/_includes/`, then use `{% include %}` in your pages so everything is kept inside the Jekyll source tree and works both locally and on GitHub Pages.
- **Auto-generate API reference**
  - Create a `Doxyfile` in the repo root.
  - In CI, run `doxygen Doxyfile` and publish its HTML into `docs/reference/api/`.
- **Re-enable Dependabot**
  - Move `archive/dependabot.yml` back into `.github/` and configure update schedules for Ruby, Actions, and GitHub Pages.
- **Flesh out the boilerplate**
  - Go through each template page (`getting-started.md`, `usage/basic-usage.md`, etc.) and fill in more thoughtfully and intentionally to guide the user through properly setting up docs for an OpenSCAD project e.g. examples, best-practice notes, etc.
- **Export and showcase models/screenshots**
  - In CI or PartCAD, call the OpenSCAD CLI to generate PNG/STL outputs and commit them into `docs/assets`.
