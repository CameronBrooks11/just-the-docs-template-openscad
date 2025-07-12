---
title: Home
layout: home
nav_order: 1
---

# {{ site.title }}

Welcome to the **{{ site.title }}** documentation!

[![Build Status](https://img.shields.io/github/actions/workflow/status/CameronBrooks11/just-the-docs-template-openscad/pages.yml?branch=main)](https://github.com/CameronBrooks11/just-the-docs-template-openscad/actions)
[![License](https://img.shields.io/github/license/CameronBrooks11/just-the-docs-template-openscad?branch=main)](https://github.com/CameronBrooks11/just-the-docs-template-openscad/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/CameronBrooks11/just-the-docs-template-openscad)](https://github.com/CameronBrooks11/just-the-docs-template-openscad/commits/main)

## Overview

This landing page should give:

1. **One-sentence elevator pitch** of your project.
2. **Badges** (build status, version, license, etc.).
3. A very brief **“What’s in this docs”** overview.
4. Links to direct users to key sections:
   - [Getting Started](getting-started)
   - [FAQ](faq)
   - [Contribute](contribute)

---

## Tips & Tricks

Below are a few of the built-in Just the Docs UI components you can sprinkle into your docs.

### Buttons

Use the `.btn` class on any link to turn it into a nicely styled button:

[Download the latest release](https://example.com/releases/latest){:.btn}

### Labels

Draw attention to status or categories with colored labels:

<span class="label label-green">Stable</span>
<span class="label label-yellow">Beta</span>
<span class="label label-purple">Experimental</span>

### Callouts

Highlight notes, tips or warnings using blockquotes:

> _These settings are experimental._

Or chose from the many built-in stylized callouts:

**An untitled callout:**

{: .highlight }
A paragraph

**A single paragraph callout:**

{: .note }
A paragraph

{: .note-title }
> My note title
>
> A paragraph with a custom title callout

**A multi-paragraph callout:**

{: .important }
> A paragraph
>
> Another paragraph
>
> The last paragraph

{: .important-title }
> My important title
>
> A paragraph
>
> Another paragraph
>
> The last paragraph

**An indented callout:**

> {: .highlight }
> A paragraph

**Indented multi-paragraph callouts:**

> {: .new }
> > A paragraph
> >
> > Another paragraph
> >
> > The last paragraph

**Nested callouts:**

{: .important }
> {: .warning }
> A paragraph

**Nested callouts with Opaque background:**

{: .important }
> {: .opaque }
> <div markdown="block">
> {: .warning }
> A paragraph
> </div>

### Tables

Markdown tables get responsive styling out-of-the-box:

| Feature       | Description                    |
| ------------- | ------------------------------ |
| Download      | Grab the latest binaries       |
| Documentation | Read the full API & tutorials  |
| Support       | Open an issue if you get stuck |

---

### Collapsible ToC

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Otherwise for a normal Table of Contents use:

> An ordered table of contents:

```
1. TOC
{:toc}
```

> An unordered table of contents:

```
- TOC
{:toc}
```

### Lists

> Unordered list:

- Item 1
- Item 2
- Item 3

_or_

- Item 1
- Item 2
- Item 3

> Ordered list:

1. Item 1
1. Item 2
1. Item 3

> Task list:

- [ ] hello, this is a todo item
- [ ] hello, this is another todo item
- [x] goodbye, this item is done

### Code Blocks

You can do inline code blocks for things like `commands and code snippets` as you normally would.

Or use syntax highlighted codeblocks, generally:
"`c" or,
"`js"

```c
length = 10;
width = 5;
height = 4;
cube([length, width, height]);
```

### Mermaid Diagrams

```mermaid
graph TD;
    accTitle: the diamond pattern
    accDescr: a graph with four nodes: A points to B and C, while B and C both point to D
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

## Just the Docs OpenSCAD Jekyll Template

This is a _bare-minimum_ template to create a Jekyll site that uses the [Just the Docs] theme. You can easily set the created site to be published on [GitHub Pages] – the [README] file explains how to do that, along with other details.

If [Jekyll] is installed on your computer, you can also build and preview the created site _locally_. This lets you test changes before committing them, and avoids waiting for GitHub Pages.[^1] And you will be able to deploy your local build to a different platform than GitHub Pages.

More specifically, the created site:

- uses a gem-based approach, i.e. uses a `Gemfile` and loads the `just-the-docs` gem
- uses the [GitHub Pages / Actions workflow] to build and publish the site on GitHub Pages

Other than that, you're free to customize sites that you create with this template, however you like. You can easily change the versions of `just-the-docs` and Jekyll it uses, as well as adding further plugins.

[Browse our documentation][Just the Docs] to learn more about how to use this theme.

To get started with creating a site, simply:

1. click "[use this template]" to create a GitHub repository
2. go to Settings > Pages > Build and deployment > Source, and select GitHub Actions

If you want to maintain your docs in the `docs` directory of an existing project repo, see [Hosting your docs from an existing project repo](https://github.com/just-the-docs/just-the-docs-template/blob/main/README.md#hosting-your-docs-from-an-existing-project-repo) in the template README.

---

[^1]: [It can take up to 10 minutes for changes to your site to publish after you push the changes to GitHub](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/creating-a-github-pages-site-with-jekyll#creating-your-site).

[Just the Docs]: https://just-the-docs.github.io/just-the-docs/
[GitHub Pages]: https://docs.github.com/en/pages
[README]: https://github.com/just-the-docs/just-the-docs-template/blob/main/README.md
[Jekyll]: https://jekyllrb.com
[GitHub Pages / Actions workflow]: https://github.blog/changelog/2022-07-27-github-pages-custom-github-actions-workflows-beta/
[use this template]: https://github.com/just-the-docs/just-the-docs-template/generate
