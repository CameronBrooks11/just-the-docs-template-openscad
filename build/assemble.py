#!/usr/bin/env python3
"""Assemble a Just the Docs source tree for an OpenSCAD repo.

usage: assemble.py --repo DIR --theme DIR --out DIR --render DIR --site-dir DIR
                   [--repository OWNER/NAME] [--base-path PATH] [--live true|false]

The repo's README.md becomes the home page; each examples/*.scad becomes an
entry on an Examples page, rendered with the OpenSCAD CLI. Files named by
docs-site.yml's `models:` key (comma-separated paths) go the same way onto a
Model page before it, for a repo whose main file is the model. Its `libraries:`
key (name=owner/repo@ref, comma-separated) names outside libraries: each is
cloned at its ref, put on OPENSCADPATH for the renders, and copied beside each
published file for the live customizer. Its `pages:` key names a folder of the
repo's own Markdown pages, published beside the generated ones, its index.md
taking the README's place as the home page. The theme (Gemfile,
styles, includes, plugins, scripts and base _config.yml) comes from --theme,
the template's own docs/ folder. Writes:

  OUT/            the Jekyll source tree
  RENDER/         rendered geometry and posters, and the staged .scad project
  RENDER/openscad-publish.yml   the openscad-web config, when there are 3D examples
  RENDER/summary.json           what was built, for the checks
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

THEME_PARTS = ["Gemfile", "Gemfile.lock", "_config.yml", "_sass", "_includes", "_plugins", "assets"]
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
# Files a live customizer may need beside the .scad sources.
PROJECT_EXT = {".scad", ".svg", ".dxf", ".stl", ".off", ".3mf", ".dat", ".json", ".png"}
SKIP_DIRS = {".git", ".github", "_site", "node_modules", "vendor", ".venv", "__pycache__"}


def read_config(repo):
    """docs-site.yml: flat 'key: value' lines only."""
    cfg = {}
    path = repo / "docs-site.yml"
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
            if m and not line.startswith("#"):
                cfg[m.group(1)] = m.group(2).strip("\"'")
    return cfg


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_config(theme_cfg, out, cfg, repository, base_path):
    owner, name = repository.split("/")
    text = theme_cfg.read_text()
    values = {
        "title": yaml_str(cfg.get("title") or name),
        "description": yaml_str(cfg.get("description", "")),
        "url": yaml_str(f"https://{owner.lower()}.github.io"),
        "baseurl": yaml_str(base_path),
        "permalink": "none",  # pages keep their paths, so relative links work as on GitHub
        "repository": yaml_str(repository),
        "color_scheme": cfg.get("color_scheme", "openscad-light"),
    }
    if cfg.get("math", "").lower() == "true":
        values["math"] = "true"
    for key, value in values.items():
        text, n = re.subn(rf"(?m)^{key}:.*$", f"{key}: {value}", text)
        if n == 0:
            text += f"\n{key}: {value}\n"
    # The theme's aux_links point at the template; a site links to its own repo.
    text = re.sub(r"(?m)^aux_links:\n(?:[ \t]+.*\n)*", "", text)
    text += f"\naux_links:\n  {yaml_str('View on GitHub')}: https://github.com/{repository}\n"
    text += "\nexclude:\n  - vendor\n  - Gemfile\n  - Gemfile.lock\n  - .jekyll-cache\n  - node_modules\n"
    (out / "_config.yml").write_text(text)


class Linker:
    """Rewrite a Markdown file's relative links for the site.

    A link is resolved against the source file's folder in the repo, and written
    relative to the built page's folder on the site. Pages in the pages folder are
    published at their path inside it, as .html; the README is the home page."""

    def __init__(self, repo, out, repository, models=(), examples=None, pages_dir=None, pages=()):
        self.repo, self.out, self.repository = repo, out, repository
        self.models = {m: model_mount(m) for m in models}
        self.examples = examples or {}
        self.pages_dir, self.pages = pages_dir, set(pages)
        self.copied = []

    def built(self, rel):
        """Where a repo file is on the site, or None if it isn't published."""
        if self.pages_dir and rel.startswith(self.pages_dir + "/") and rel in self.pages:
            return rel[len(self.pages_dir) + 1:][:-len(".md")] + ".html"
        return None

    def target(self, link, base="", page_dir=""):
        if not link or re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/|^\{\{", link, re.I):
            return link
        path, _, anchor = link.partition("#")
        anchor = "#" + anchor if anchor else ""
        rel = os.path.normpath(os.path.join(base, path))
        if rel.startswith(".."):
            return link

        def here(site_path):
            return os.path.relpath(site_path, page_dir or ".") if page_dir else site_path

        src = self.repo / rel
        if rel in ("README.md", "."):
            return here("index.html") + anchor
        page = self.built(rel)
        if page:
            return here(page) + anchor
        if self.pages_dir and rel.startswith(self.pages_dir + "/"):
            # Anything else inside the pages folder is copied as it is, so it keeps its path.
            if src.is_file() and src.suffix != ".md":
                return here(rel[len(self.pages_dir) + 1:]) + anchor
        if src.is_file() and src.suffix.lower() in IMAGE_EXT:
            dest = self.out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if rel not in self.copied:
                self.copied.append(rel)
            return here(rel) + anchor
        if rel in self.models:
            return here("model.html") + "#" + self.models[rel]
        if rel in self.examples:
            return here("examples.html") + "#" + self.examples[rel]
        if rel == "examples" and self.examples:
            # The folder on GitHub; on the site, the page that shows it.
            return here("examples.html") + anchor
        kind = "tree" if src.is_dir() else "blob"
        return f"https://github.com/{self.repository}/{kind}/HEAD/{rel}{anchor}"

    def rewrite(self, md, base="", page_dir=""):
        """Rewrite links outside fenced code blocks, where they are literal text."""
        parts = re.split(r"(?ms)(^[ \t]*(?:```|~~~).*?^[ \t]*(?:```|~~~)[ \t]*$)", md)
        return "".join(p if i % 2 else self.rewrite_text(p, base, page_dir) for i, p in enumerate(parts))

    def rewrite_text(self, md, base="", page_dir=""):
        t = lambda link: self.target(link, base, page_dir)
        # Markdown links and images: [text](target "title") and ![alt](target)
        md = re.sub(r"(\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))", lambda m: m.group(1) + t(m.group(2)) + m.group(3), md)
        # Reference definitions: [label]: target
        md = re.sub(r"(?m)^(\s*\[[^\]]+\]:\s*)(\S+)", lambda m: m.group(1) + t(m.group(2)), md)
        # HTML attributes
        md = re.sub(r"((?:src|href)=\")([^\"]+)(\")", lambda m: m.group(1) + t(m.group(2)) + m.group(3), md)
        return md


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def model_mount(rel):
    """A model's mount and anchor: prefixed, so it cannot meet an example's."""
    return "model-" + slug(rel[:-len(".scad")])


def read_models(repo, cfg):
    """The models: key's paths, each a .scad file inside the repo."""
    models = []
    for m in (p.strip() for p in cfg.get("models", "").split(",")):
        if not m:
            continue
        rel = os.path.normpath(m)
        if rel.startswith("..") or os.path.isabs(rel) or not rel.endswith(".scad") or not (repo / rel).is_file():
            sys.exit(f"docs-site.yml models: {m} is not a .scad file in the repo")
        models.append(Path(rel).as_posix())
    return models


def find_examples(repo):
    """examples/*.scad; or, when there are none at the top, examples/<folder>/**.scad,
    grouped by folder. A repo with both keeps only the top level, so folders of data
    files that examples include (pixelArtSCAD's examples/art) stay out."""
    d = repo / "examples"
    if not d.is_dir():
        return []
    top = sorted(d.glob("*.scad"))
    if top:
        return top
    return sorted(p for p in d.rglob("*.scad") if not any(s.startswith((".", "_")) for s in p.relative_to(d).parts))


def example_slug(repo, ex):
    """An example's mount and anchor, from its path inside examples/. Kramdown takes a
    heading id only if it starts with a letter, so 01_elbow is example-01-elbow."""
    s = slug(ex.relative_to(repo / "examples").with_suffix("").as_posix())
    return "example-" + s if s[:1].isdigit() else s


PAGE_SKIP_DIRS = SKIP_DIRS | {".jekyll-cache", ".bundle"}


def read_pages(repo, cfg):
    """The pages: folder and its Markdown pages (repo-relative), or (None, [])."""
    d = cfg.get("pages", "").strip().strip("/")
    if not d:
        return None, []
    rel = os.path.normpath(d)
    if rel.startswith("..") or os.path.isabs(rel) or not (repo / rel).is_dir():
        sys.exit(f"docs-site.yml pages: {d} is not a folder in the repo")
    pages = []
    for root, dirs, files in os.walk(repo / rel):
        dirs[:] = sorted(x for x in dirs if x not in PAGE_SKIP_DIRS and not x.startswith(("_", ".")))
        for f in sorted(files):
            # A README in the pages folder describes the folder on GitHub; it isn't a page.
            if f.endswith(".md") and f != "README.md":
                pages.append((Path(root) / f).relative_to(repo).as_posix())
    return Path(rel).as_posix(), pages


def publish_pages(repo, out, pages_dir, pages, linker):
    """Copy the pages folder into the site: each page with its links rewritten, and the
    files beside them (images and the like) as they are. Folders starting with _ or . are
    skipped, and a file the engine already wrote (its _config.yml, Gemfile, scripts) is
    never replaced, so an old copy of the theme left in the folder has no effect."""
    src = repo / pages_dir
    for root, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if x not in PAGE_SKIP_DIRS and not x.startswith(("_", "."))]
        for f in files:
            p = Path(root) / f
            inner = p.relative_to(src).as_posix()
            rel = p.relative_to(repo).as_posix()
            dest = out / inner
            if rel in pages:
                text = p.read_text()
                m = re.match(r"(?s)(---\n.*?\n---\n)(.*)", text)
                front, body = (m.group(1), m.group(2)) if m else ("", text)
                body = linker.rewrite(body, base=os.path.dirname(rel), page_dir=os.path.dirname(inner))
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(front + body)
            elif p.suffix != ".md" and not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)


# Loaded on pages whose front matter sets math: true, or on every page when docs-site.yml
# does. Inline math is $…$, as on GitHub; MathJax doesn't read single dollars unless told to.
MATHJAX = """{%- if page.math or site.math %}
<script>
  window.MathJax = { tex: { inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]] } };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>
{%- endif %}
"""


LIBRARY = re.compile(r"^([A-Za-z0-9_.-]+)=([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([A-Za-z0-9_./-]+)$")


def read_libraries(cfg):
    """The libraries: key's entries, each name=owner/repo@ref, as (name, owner/repo, ref)."""
    libs = []
    for entry in (p.strip() for p in cfg.get("libraries", "").split(",")):
        if not entry:
            continue
        m = LIBRARY.match(entry)
        if not m or m.group(1) in (".", ".."):
            sys.exit(f"docs-site.yml libraries: {entry} is not name=owner/repo@ref")
        libs.append(m.groups())
    return libs


def fetch_libraries(libs, libs_dir):
    """Clone each library from GitHub at its ref into libs_dir/<name>."""
    for name, source, ref in libs:
        dest = libs_dir / name
        url = f"https://github.com/{source}.git"
        steps = [["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", url, str(dest)],
                 ["git", "-C", str(dest), "checkout", "--quiet", "--detach", ref]]
        for cmd in steps:
            r = run(cmd, libs_dir, timeout=300)
            if r.returncode != 0:
                sys.exit(f"could not fetch library {name} from {source} at {ref}:\n{r.stdout}{r.stderr}")


def stage_libraries(libs_dir, libs, stage, entries):
    """Copy each library into the live customizer's project beside every entry, as
    openscad-web resolves an include relative to the including file."""
    for d in sorted({Path(e).parent for e in entries}):
        for name, _, _ in libs:
            if (stage / d / name).exists():
                sys.exit(f"library {name} would overwrite {d / name} in the repo")
            stage_project(libs_dir / name, stage / d / name)


def leading_comment(scad_text):
    """The comment lines at the top of an example: its title and description."""
    lines = []
    for line in scad_text.splitlines():
        s = line.strip()
        if s.startswith("//"):
            lines.append(s[2:].strip())
        elif s == "" and not lines:
            continue
        else:
            break
    return lines


def title_and_body(lines):
    """Split a leading comment into a title and a description.

    The title is the first sentence, however many lines it wraps over. A first line
    with no closing punctuation, followed by one that starts with a capital, is a
    title on its own line, as in "A rounded block" over "The library's one module".
    """
    title, rest = [], []
    for i, line in enumerate(lines):
        if rest:
            rest.append(line)
            continue
        title.append(line)
        joined = " ".join(title)
        m = re.search(r"[.!?](\s+|$)", joined)
        if m:
            tail = joined[m.end():].strip()
            title, rest = [joined[:m.end()].strip()], ([tail] if tail else [""])
            continue
        if i + 1 < len(lines) and lines[i + 1][:1].isupper():
            rest = [""]
    return " ".join(title), " ".join(r for r in rest if r)


def run(cmd, cwd, timeout=600):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"timed out after {timeout} s: {' '.join(cmd[:2])}")


def render(repo, example, render_dir, name):
    """Render one file as NAME.off and NAME.png: OFF + poster for 3D, a picture for 2D."""
    rel = example.relative_to(repo)
    off = render_dir / f"{name}.off"
    png = render_dir / f"{name}.png"
    r = run(["openscad", "-o", str(off), str(rel)], repo)
    is3d = r.returncode == 0 and off.exists() and off.stat().st_size > 0
    if not is3d:
        out = r.stdout + r.stderr
        if "not a 3D object" not in out:
            sys.exit(f"openscad failed on {rel}:\n{out}")
    # Preview mode keeps color(); a dark scheme suits the viewer it sits in. A
    # current OpenSCAD renders offscreen; an older one (as apt has) needs a
    # display, so xvfb-run is the fallback rather than the default. Where Xvfb
    # cannot start (a read-only /tmp, as in a sandbox) xvfb-run waits forever,
    # so the fallback has a timeout.
    pic = ["openscad", "-o", str(png), "--imgsize=1000,750", "--viewall", "--autocenter",
           "--colorscheme=Tomorrow Night", str(rel)]
    p = run(pic, repo)
    if (p.returncode != 0 or not png.exists()) and shutil.which("xvfb-run"):
        p = run(["xvfb-run", "-a"] + pic, repo, timeout=120)
    if p.returncode != 0 or not png.exists():
        sys.exit(f"openscad could not render a picture of {rel}:\n{p.stdout}{p.stderr}")
    return is3d


def stage_project(repo, stage):
    """Copy the files a live customizer may need, keeping their paths."""
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in PROJECT_EXT:
                dest = stage / p.relative_to(repo)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--theme", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--render", required=True, type=Path)
    ap.add_argument("--site-dir", required=True, type=Path)
    ap.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--base-path", default=None)
    ap.add_argument("--live", default="true")
    a = ap.parse_args()

    repo, out, render_dir = a.repo.resolve(), a.out.resolve(), a.render.resolve()
    if not (repo / "README.md").is_file():
        sys.exit(f"{repo} has no README.md")
    if "/" not in a.repository:
        sys.exit("--repository OWNER/NAME is required outside GitHub Actions")
    name = a.repository.split("/")[1]
    base_path = a.base_path if a.base_path is not None else ("" if name.lower().endswith(".github.io") else "/" + name)
    cfg = read_config(repo)
    live = a.live.lower() == "true" and cfg.get("live", "true").lower() == "true"
    models = read_models(repo, cfg)
    libs = read_libraries(cfg)

    for d in (out, render_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    # Libraries are fetched beside the render output, and put on OpenSCAD's library
    # path for every render below.
    libs_dir = render_dir / "libraries"
    if libs:
        libs_dir.mkdir()
        fetch_libraries(libs, libs_dir)
        os.environ["OPENSCADPATH"] = os.pathsep.join(
            p for p in (str(libs_dir), os.environ.get("OPENSCADPATH", "")) if p)
    for part in THEME_PARTS:
        src = a.theme / part
        if src.is_dir():
            shutil.copytree(src, out / part)
        elif src.is_file():
            shutil.copy2(src, out / part)
    write_config(a.theme / "_config.yml", out, cfg, a.repository, base_path)

    # examples: none leaves examples/ to the repo, for one whose examples a page of its
    # own shows better (drawing sheets, say) or whose folder holds included helpers.
    examples = [] if cfg.get("examples", "").strip().lower() == "none" else find_examples(repo)
    ex_slugs = {ex.relative_to(repo).as_posix(): example_slug(repo, ex) for ex in examples}
    pages_dir, pages = read_pages(repo, cfg)
    linker = Linker(repo, out, a.repository, models, ex_slugs, pages_dir, pages)
    home_page = f"{pages_dir}/index.md" in pages if pages_dir else False
    if not home_page:
        readme = linker.rewrite((repo / "README.md").read_text())
        # raw: a README is plain Markdown, and Liquid must not read its braces.
        (out / "index.md").write_text("---\ntitle: Home\nlayout: default\nnav_order: 1\npermalink: /\n---\n\n"
                                      "{% raw %}\n" + readme.rstrip() + "\n{% endraw %}\n")
    if pages_dir:
        publish_pages(repo, out, pages_dir, pages, linker)
    if not (out / "_includes" / "head_custom.html").exists():
        (out / "_includes").mkdir(exist_ok=True)
        (out / "_includes" / "head_custom.html").write_text(MATHJAX)

    summary = {"base_path": base_path, "images": linker.copied, "models": [], "examples": [], "targets": [],
               "pages": [linker.built(p) for p in pages]}
    targets = []

    def section(src, title, body, mount, heading=None, level=2):
        """Render one file, add its mounts, and return its page section."""
        rel = src.relative_to(repo).as_posix()
        live_mount = mount + "-live"
        is3d = render(repo, src, render_dir, mount)
        sec = [f"{'#' * level} {heading or title} {{#{mount}}}", "", body, ""]
        if is3d:
            targets.append(f"  - surface: static\n    geometry: ./{mount}.off\n    poster: ./{mount}.png\n"
                           f"    mountPath: /models/{mount}/\n    title: {yaml_str(title)}\n")
            summary["targets"].append(f"models/{mount}")
            if live:
                targets.append(f"  - surface: customizer\n    projectRoot: ./project\n"
                               f"    entry: ./{rel}\n    mountPath: /models/{live_mount}/\n"
                               f"    controls: true\n    download: true\n    title: {yaml_str(title + ' (interactive)')}\n")
                summary["targets"].append(f"models/{live_mount}")
            live_arg = f' live="{live_mount}"' if live else ""
            sec.append(f'{{% include openscad.html model="{mount}"{live_arg} title={yaml_str(title)} %}}')
        else:
            pic = f"assets/examples/{mount}.png"
            (out / "assets/examples").mkdir(parents=True, exist_ok=True)
            shutil.copy2(render_dir / f"{mount}.png", out / pic)
            sec.append(f"![{title}]({pic})")
        sec += ["", "<details markdown=\"1\">", f"<summary>Source: {rel}</summary>", "",
                "{% raw %}", "```openscad", src.read_text().rstrip(), "```", "{% endraw %}", "", "</details>", "",
                f"[{rel} on GitHub](https://github.com/{a.repository}/blob/HEAD/{rel})", ""]
        return "\n".join(sec), is3d

    if models or examples:
        stage_project(repo, render_dir / "project")
        if libs:
            entries = models + [ex.relative_to(repo).as_posix() for ex in examples]
            stage_libraries(libs_dir, libs, render_dir / "project", entries)
    summary["libraries"] = [name for name, _, _ in libs]
    # A repo's own pages come first in the navigation, then the Model and Examples pages.
    nav = 1000 if pages_dir else 2
    if models:
        sections = []
        for m in models:
            # A model's own header comment is often a file banner, so its path is its title.
            text, is3d = section(repo / m, m, "", model_mount(m), heading=f"`{m}`")
            sections.append(text)
            summary["models"].append({"path": m, "slug": model_mount(m), "is3d": is3d})
        title = "Model" if len(models) == 1 else "Models"
        header = f"---\ntitle: {title}\nlayout: default\nnav_order: {nav}\n---\n\n# {title}\n\n"
        (out / "model.md").write_text(header + "\n".join(sections))
        nav += 1
    if examples:
        sections = []
        grouped = any(ex.parent != repo / "examples" for ex in examples)
        group = None
        for ex in examples:
            if grouped and ex.parent != group:
                group = ex.parent
                sections.append(f"## {group.relative_to(repo / 'examples').as_posix()}\n")
            comment = leading_comment(ex.read_text())
            title, body = title_and_body(comment) if comment else (ex.stem.replace("_", " "), "")
            mount = ex_slugs[ex.relative_to(repo).as_posix()]
            text, is3d = section(ex, title, body, mount, level=3 if grouped else 2)
            sections.append(text)
            summary["examples"].append({"name": ex.relative_to(repo / "examples").with_suffix("").as_posix(),
                                        "slug": mount, "is3d": is3d})
        header = f"---\ntitle: Examples\nlayout: default\nnav_order: {nav}\n---\n\n# Examples\n\n"
        (out / "examples.md").write_text(header + "\n".join(sections))
    if targets:
        (render_dir / "openscad-publish.yml").write_text(
            f"site:\n  outDir: {a.site_dir.resolve()}\n\ntargets:\n" + "".join(targets))
    (render_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"assembled {out}: home page, {len(models)} models, {len(examples)} examples "
          f"({sum(e['is3d'] for e in summary['models'] + summary['examples'])} in 3D), "
          f"{len(linker.copied)} images; base path '{base_path}'")


if __name__ == "__main__":
    main()
