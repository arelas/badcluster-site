# badcluster.dev

Source for the Bad Cluster site. Static HTML/CSS, no JS framework, no
build tooling beyond a small Python script that generates the blog pages
from Markdown.

## Structure

```
index.html          Generated - home page (don't hand-edit, see build.py)
styles.css           Shared stylesheet for every page
assets/              Images
blog/                Generated - blog index + one folder per post
contact/             Generated - contact page
posts/               Source - Markdown files, one per blog post
build.py             Regenerates index.html, blog/, and contact/ from
                     the content below and posts/*.md
CNAME                GitHub Pages custom domain config (badcluster.dev)
```

Anything under `blog/` or `contact/`, plus `index.html` itself, is build
output. Hand-editing those will work until the next `python3 build.py`,
which overwrites them. Edit `posts/*.md` for blog content, or `build.py`
itself for the home page, header/footer, or page templates.

## Adding a blog post

Create a new file in `posts/`, named however you like (the date in the
filename is just for sorting convenience - the real date comes from
frontmatter). Format:

```markdown
---
title: Your Post Title
date: 2026-07-04
summary: One sentence, shown on the blog index page.
---

Body in Markdown from here on. Headings, links, lists, `inline code`,
and fenced code blocks all work.
```

Then rebuild:

```bash
python3 build.py
```

Requires the `markdown` package: `pip install markdown`.

## Editing the home page or templates

The home page content, header, footer, and page shell are all defined as
Python strings in `build.py` (see `build_home()`, `render_header()`,
`render_footer()`, `page_shell()`). Edit those, then rerun the build.

## Contact form

The contact form posts to [Formspree](https://formspree.io). To make it
actually deliver messages to you:

1. Create a free account at formspree.io and add a new form.
2. Copy the form endpoint URL it gives you (looks like
   `https://formspree.io/f/abcd1234`).
3. In `build.py`, replace the `FORM_ACTION` placeholder with that URL.
4. Rerun `python3 build.py` and redeploy.

Until that's done, the form is wired up correctly but has nowhere real to
send to - `build.py` will print a reminder every time you build if the
placeholder is still in place.

## Local preview

Browser security blocks the page's absolute paths (`/styles.css`, etc.)
when opened directly as a `file://` URL. Serve it locally instead:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

## Deploying

Pushed to GitHub Pages. `CNAME` is already set to `badcluster.dev`; in
the repo's Settings → Pages, set the source to this branch. Since
badcluster.dev is an apex/root domain, your DNS provider needs A records
pointing at GitHub Pages' IPs (185.199.108.153, .109.153, .110.153,
.111.153) rather than a plain CNAME.
