#!/usr/bin/env python3
"""Assemble a Just the Docs source tree for an OpenSCAD repo.

usage: assemble.py --repo DIR --theme DIR --out DIR --render DIR --site-dir DIR
                   [--repository OWNER/NAME] [--base-path PATH] [--live true|false]

The repo's README.md becomes the home page; each examples/*.scad becomes an
entry on an Examples page, rendered with the OpenSCAD CLI. The theme (Gemfile,
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
    """Rewrite the README's relative links for the site."""

    def __init__(self, repo, out, repository):
        self.repo, self.out, self.repository = repo, out, repository
        self.copied = []

    def target(self, link):
        if not link or re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/|^\{\{", link, re.I):
            return link
        path, _, anchor = link.partition("#")
        anchor = "#" + anchor if anchor else ""
        rel = os.path.normpath(path)
        if rel.startswith(".."):
            return link
        src = self.repo / rel
        if rel in ("README.md", "."):
            return "index.html" + anchor
        if src.is_file() and src.suffix.lower() in IMAGE_EXT:
            dest = self.out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            if rel not in self.copied:
                self.copied.append(rel)
            return rel + anchor
        if rel.startswith("examples/") and src.suffix == ".scad":
            return "examples.html#" + slug(src.stem)
        kind = "tree" if src.is_dir() else "blob"
        return f"https://github.com/{self.repository}/{kind}/HEAD/{rel}{anchor}"

    def rewrite(self, md):
        """Rewrite links outside fenced code blocks, where they are literal text."""
        parts = re.split(r"(?ms)(^[ \t]*(?:```|~~~).*?^[ \t]*(?:```|~~~)[ \t]*$)", md)
        return "".join(p if i % 2 else self.rewrite_text(p) for i, p in enumerate(parts))

    def rewrite_text(self, md):
        # Markdown links and images: [text](target "title") and ![alt](target)
        md = re.sub(r"(\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))",
                    lambda m: m.group(1) + self.target(m.group(2)) + m.group(3), md)
        # Reference definitions: [label]: target
        md = re.sub(r"(?m)^(\s*\[[^\]]+\]:\s*)(\S+)", lambda m: m.group(1) + self.target(m.group(2)), md)
        # HTML attributes
        md = re.sub(r"((?:src|href)=\")([^\"]+)(\")", lambda m: m.group(1) + self.target(m.group(2)) + m.group(3), md)
        return md


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


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


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def render(repo, example, render_dir):
    """Render one example: OFF + poster for 3D, a picture for 2D."""
    rel = example.relative_to(repo)
    off = render_dir / f"{example.stem}.off"
    png = render_dir / f"{example.stem}.png"
    r = run(["openscad", "-o", str(off), str(rel)], repo)
    is3d = r.returncode == 0 and off.exists() and off.stat().st_size > 0
    if not is3d:
        out = r.stdout + r.stderr
        if "not a 3D object" not in out:
            sys.exit(f"openscad failed on {rel}:\n{out}")
    # Preview mode keeps color(); a dark scheme suits the viewer it sits in. A
    # current OpenSCAD renders offscreen; an older one (as apt has) needs a
    # display, so xvfb-run is the fallback rather than the default.
    pic = ["openscad", "-o", str(png), "--imgsize=1000,750", "--viewall", "--autocenter",
           "--colorscheme=Tomorrow Night", str(rel)]
    p = run(pic, repo)
    if (p.returncode != 0 or not png.exists()) and shutil.which("xvfb-run"):
        p = run(["xvfb-run", "-a"] + pic, repo)
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

    for d in (out, render_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for part in THEME_PARTS:
        src = a.theme / part
        if src.is_dir():
            shutil.copytree(src, out / part)
        elif src.is_file():
            shutil.copy2(src, out / part)
    write_config(a.theme / "_config.yml", out, cfg, a.repository, base_path)

    linker = Linker(repo, out, a.repository)
    readme = linker.rewrite((repo / "README.md").read_text())
    # raw: a README is plain Markdown, and Liquid must not read its braces.
    (out / "index.md").write_text("---\ntitle: Home\nlayout: default\nnav_order: 1\npermalink: /\n---\n\n"
                                  "{% raw %}\n" + readme.rstrip() + "\n{% endraw %}\n")

    examples = sorted((repo / "examples").glob("*.scad")) if (repo / "examples").is_dir() else []
    summary = {"base_path": base_path, "images": linker.copied, "examples": [], "targets": []}
    if examples:
        stage = render_dir / "project"
        stage_project(repo, stage)
        targets, sections = [], []
        for ex in examples:
            is3d = render(repo, ex, render_dir)
            text = ex.read_text()
            comment = leading_comment(text)
            title = comment[0] if comment else ex.stem.replace("_", " ")
            body = " ".join(comment[1:])
            mount, live_mount = slug(ex.stem), slug(ex.stem) + "-live"
            sec = [f"## {title} {{#{mount}}}", "", body, ""]
            if is3d:
                targets.append(f"  - surface: static\n    geometry: ./{ex.stem}.off\n    poster: ./{ex.stem}.png\n"
                               f"    mountPath: /models/{mount}/\n    title: {yaml_str(title)}\n")
                if live:
                    targets.append(f"  - surface: customizer\n    projectRoot: ./project\n"
                                   f"    entry: ./{ex.relative_to(repo).as_posix()}\n    mountPath: /models/{live_mount}/\n"
                                   f"    controls: true\n    download: true\n    title: {yaml_str(title + ' (interactive)')}\n")
                live_arg = f' live="{live_mount}"' if live else ""
                sec.append(f'{{% include openscad.html model="{mount}"{live_arg} title={yaml_str(title)} %}}')
            else:
                pic = f"assets/examples/{ex.stem}.png"
                (out / "assets/examples").mkdir(parents=True, exist_ok=True)
                shutil.copy2(render_dir / f"{ex.stem}.png", out / pic)
                sec.append(f"![{title}]({pic})")
            rel = ex.relative_to(repo).as_posix()
            sec += ["", "<details markdown=\"1\">", f"<summary>Source: {rel}</summary>", "",
                    "{% raw %}", "```openscad", text.rstrip(), "```", "{% endraw %}", "", "</details>", "",
                    f"[{rel} on GitHub](https://github.com/{a.repository}/blob/HEAD/{rel})", ""]
            sections.append("\n".join(s for s in sec if s is not None))
            summary["examples"].append({"name": ex.stem, "slug": mount, "is3d": is3d})
            if is3d:
                summary["targets"].append(f"models/{mount}")
                if live:
                    summary["targets"].append(f"models/{live_mount}")
        header = "---\ntitle: Examples\nlayout: default\nnav_order: 2\n---\n\n# Examples\n\n"
        (out / "examples.md").write_text(header + "\n".join(sections))
        if targets:
            (render_dir / "openscad-publish.yml").write_text(
                f"site:\n  outDir: {a.site_dir.resolve()}\n\ntargets:\n" + "".join(targets))
    (render_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"assembled {out}: home page, {len(examples)} examples "
          f"({sum(e['is3d'] for e in summary['examples'])} in 3D), {len(linker.copied)} images; base path '{base_path}'")


if __name__ == "__main__":
    main()
