#!/usr/bin/env python3
"""
Bad Cluster site builder.

Regenerates index.html, blog/index.html, blog/<slug>/index.html, and
contact/index.html from the templates and content below. Blog posts are
authored as Markdown files in posts/ with a small frontmatter block.

Usage:
    python3 build.py

To add a new post: drop a new posts/<anything>.md file (see
posts/0001-hello-bad-cluster.md for the format), then rerun this script.
Generated HTML under blog/ is build output - don't hand-edit it, since the
next build will overwrite it.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

try:
    import markdown as md
except ImportError:
    sys.exit("Missing dependency: pip install markdown")

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
BLOG_DIR = ROOT / "blog"
CONTACT_DIR = ROOT / "contact"

SITE_NAME = "Bad Cluster"
SITE_URL = "https://badcluster.dev"
GITHUB_URL = "https://github.com/arelas"

# TODO: replace with your real Formspree (or similar) endpoint once you've
# created a free account at https://formspree.io and made a form there.
FORM_ACTION = "https://formspree.io/f/mzdlaayv"


# ---- Shared page chrome ----------------------------------------------------

def render_header(active=""):
    def link(href, label, key):
        cls = "nav-link is-active" if key == active else "nav-link"
        return f'<a class="{cls}" href="{href}">{label}</a>'

    return f"""<header>
  <div class="header-inner">
    <a class="wordmark" href="/"><span class="dot" aria-hidden="true"></span>{SITE_NAME.upper()}</a>
    <button class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="primaryNav">MENU</button>
    <nav class="nav" id="primaryNav">
      <div class="nav-links">
        {link("/#projects", "PROJECTS", "projects")}
        {link("/blog/", "BLOG", "blog")}
        {link("/contact/", "CONTACT", "contact")}
      </div>
      <div class="nav-divider" aria-hidden="true"></div>
      <a class="nav-link" href="{GITHUB_URL}" target="_blank" rel="noopener">GITHUB &#8599;</a>
    </nav>
  </div>
</header>
<script>
  document.getElementById('navToggle').addEventListener('click', function () {{
    var nav = document.getElementById('primaryNav');
    var open = nav.classList.toggle('is-open');
    this.setAttribute('aria-expanded', open ? 'true' : 'false');
  }});
</script>"""


def render_footer():
    year = datetime.now().year
    return f"""<footer>
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="wordmark" href="/"><span class="dot" aria-hidden="true"></span>{SITE_NAME.upper()}</a>
      <p class="footer-tagline">A disk doesn't lie about which sectors are bad. We'd like our software to be just as honest.</p>
    </div>
    <div class="footer-col">
      <p class="footer-col-head">SITE</p>
      <a href="/#projects">Projects</a>
      <a href="/blog/">Blog</a>
      <a href="/contact/">Contact</a>
    </div>
    <div class="footer-col">
      <p class="footer-col-head">ELSEWHERE</p>
      <a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub &#8599;</a>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>&copy; {year} {SITE_NAME.upper()}</span>
    <span class="footer-marker">0x00000000 // EOF</span>
  </div>
</footer>"""


def page_shell(title, description, body_html, active="", canonical=""):
    canonical_tag = f'<link rel="canonical" href="{SITE_URL}{canonical}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
{canonical_tag}
<link rel="icon" href="/assets/phat32-icon.png">
<link rel="stylesheet" href="/styles.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
{render_header(active)}
<main>
{body_html}
</main>
{render_footer()}
</body>
</html>
"""


# ---- Frontmatter parsing ----------------------------------------------------

def parse_post(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        sys.exit(f"{path.name}: missing --- frontmatter block")

    frontmatter_raw, body_md = m.group(1), m.group(2)
    meta = {}
    for line in frontmatter_raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()

    for required in ("title", "date", "summary"):
        if required not in meta:
            sys.exit(f"{path.name}: frontmatter missing '{required}:'")

    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    date_obj = datetime.strptime(meta["date"], "%Y-%m-%d")

    body_html = md.markdown(body_md.strip(), extensions=["fenced_code", "tables"])

    return {
        "slug": slug,
        "title": meta["title"],
        "date": date_obj,
        "date_str": date_obj.strftime("%B %-d, %Y") if sys.platform != "win32" else date_obj.strftime("%B %d, %Y"),
        "summary": meta["summary"],
        "body_html": body_html,
    }


# ---- Page builders ----------------------------------------------------------

def build_post_page(post):
    out_dir = BLOG_DIR / post["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    body = f"""
<article class="wrap-narrow">
  <div class="post-header">
    <a class="back-link" href="/blog/">&larr; Back to blog</a>
    <p class="post-meta">{post['date_str']}</p>
    <h1 class="post-title">{post['title']}</h1>
  </div>
  <div class="post-body">
{post['body_html']}
  </div>
</article>
"""
    html = page_shell(
        title=f"{post['title']} - {SITE_NAME}",
        description=post["summary"],
        body_html=body,
        active="blog",
        canonical=f"/blog/{post['slug']}/",
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  blog/{post['slug']}/index.html")


def build_blog_index(posts):
    if posts:
        items = "\n".join(f"""
      <a class="post-item" href="/blog/{p['slug']}/">
        <span class="post-meta">{p['date_str']}</span>
        <span class="post-item-title">{p['title']}</span>
        <span class="post-item-summary">{p['summary']}</span>
      </a>""" for p in posts)
        list_html = f'<div class="post-list">{items}\n    </div>'
    else:
        list_html = '<p class="empty-blog">[ cluster free ] Nothing posted yet.</p>'

    body = f"""
<section class="page-hero wrap">
  <p class="eyebrow">0xFFFFFFFE &nbsp;//&nbsp; LOG</p>
  <h1>Blog</h1>
  <p class="hero-sub">Notes on what we're building and why, written as it happens.</p>
</section>
<section class="block wrap-narrow">
  {list_html}
</section>
"""
    html = page_shell(
        title=f"Blog - {SITE_NAME}",
        description="Notes on what Bad Cluster is building and why.",
        body_html=body,
        active="blog",
        canonical="/blog/",
    )
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    (BLOG_DIR / "index.html").write_text(html, encoding="utf-8")
    print("  blog/index.html")


def build_contact_page():
    body = f"""
<section class="page-hero wrap">
  <p class="eyebrow">0x00000001 &nbsp;//&nbsp; OPEN CHANNEL</p>
  <h1>Get in touch</h1>
  <p class="hero-sub">Question, bug report, idea, or just want to say hello - this goes straight to us.</p>
</section>
<section class="form-block wrap">
  <form class="contact-form" id="contactForm" action="{FORM_ACTION}" method="POST">
    <div class="field">
      <label for="name">Name</label>
      <input id="name" name="name" type="text" placeholder="Your name" required>
    </div>
    <div class="field">
      <label for="email">Email</label>
      <input id="email" name="email" type="email" placeholder="you@example.com" required>
    </div>
    <div class="field">
      <label for="message">Message</label>
      <textarea id="message" name="message" rows="6" placeholder="What's on your mind?" required></textarea>
    </div>
    <button class="btn-submit" type="submit" id="contactSubmit">Send message</button>
    <p class="form-note" id="contactNote">Sent via Formspree. We don't store this anywhere ourselves.</p>
  </form>
  <div class="form-success" id="contactSuccess" hidden>
    Message sent. We'll get back to you soon.
  </div>
</section>
<script>
  (function () {{
    var form = document.getElementById('contactForm');
    var button = document.getElementById('contactSubmit');
    var note = document.getElementById('contactNote');
    var success = document.getElementById('contactSuccess');

    form.addEventListener('submit', function (e) {{
      e.preventDefault();
      button.disabled = true;
      button.textContent = 'Sending...';
      note.textContent = '';

      fetch(form.action, {{
        method: 'POST',
        body: new FormData(form),
        headers: {{ 'Accept': 'application/json' }}
      }}).then(function (response) {{
        if (response.ok) {{
          form.hidden = true;
          success.hidden = false;
        }} else {{
          response.json().then(function (data) {{
            var msg = (data && data.errors && data.errors.length)
              ? data.errors.map(function (er) {{ return er.message; }}).join(', ')
              : 'Something went wrong. Please try again.';
            note.textContent = msg;
            note.style.color = 'var(--accent-copper)';
            button.disabled = false;
            button.textContent = 'Send message';
          }});
        }}
      }}).catch(function () {{
        note.textContent = 'Something went wrong. Please check your connection and try again.';
        note.style.color = 'var(--accent-copper)';
        button.disabled = false;
        button.textContent = 'Send message';
      }});
    }});
  }})();
</script>
"""
    html = page_shell(
        title=f"Contact - {SITE_NAME}",
        description="Get in touch with Bad Cluster.",
        body_html=body,
        active="contact",
        canonical="/contact/",
    )
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    (CONTACT_DIR / "index.html").write_text(html, encoding="utf-8")
    print("  contact/index.html")


def build_home(posts):
    recent_posts = posts[:2]

    if recent_posts:
        preview_items = "\n".join(f"""
      <a class="post-item" href="/blog/{p['slug']}/">
        <span class="post-meta">{p['date_str']}</span>
        <span class="post-item-title">{p['title']}</span>
        <span class="post-item-summary">{p['summary']}</span>
      </a>""" for p in recent_posts)
        blog_preview_section = f"""
<section class="block wrap">
  <div class="section-head">
    <div>
      <p class="section-eyebrow">LOG // {len(posts)} ENTR{"Y" if len(posts) == 1 else "IES"}</p>
      <h2>From the blog.</h2>
    </div>
    <a class="section-link" href="/blog/">All posts &#8594;</a>
  </div>
  <div class="post-list">{preview_items}
  </div>
</section>
"""
    else:
        blog_preview_section = ""

    body = """
<section class="hero wrap">
  <p class="eyebrow">0x0FFFFFF7 &nbsp;//&nbsp; THE BAD_CLUSTER MARKER</p>
  <h1>A disk doesn't lie about which sectors are bad.<span class="hero-cursor" aria-hidden="true"></span><br><span class="dim">We'd like our software to be just as honest.</span></h1>
  <p class="hero-sub">Whatever we end up building &mdash; tools, sites, something else entirely &mdash; if we find it useful, we put it out into the world.</p>

  <div class="sector-grid" aria-hidden="true">
""" + "\n".join(_sector_grid_cells()) + """
  </div>
  <p class="sector-caption">144 clusters scanned &middot; 4 marked bad &middot; the rest are fine</p>
</section>

<section class="block wrap" id="approach">
  <div class="section-head">
    <div>
      <p class="section-eyebrow">0xFFFFFFF8 &nbsp;//&nbsp; MEDIA DESCRIPTOR</p>
      <h2>How we work.</h2>
    </div>
  </div>

  <div class="principle-grid">
    <div class="principle">
      <span class="principle-marker">01</span>
      <h3>Mark it, don't hide it</h3>
      <p>If something doesn't work, we say so - in the docs, in the UI, in the code comments. A known limitation beats a confident lie every time.</p>
    </div>
    <div class="principle">
      <span class="principle-marker">02</span>
      <h3>Built because we needed it</h3>
      <p>Everything here started as a real problem one of us actually had. Nothing is built speculatively for an audience that doesn't exist yet.</p>
    </div>
    <div class="principle">
      <span class="principle-marker">03</span>
      <h3>Open by default</h3>
      <p>Source, build process, and the reasoning behind decisions are public unless there's a specific reason they can't be.</p>
    </div>
  </div>
</section>

<section class="block wrap" id="projects">
  <div class="section-head">
    <div>
      <p class="section-eyebrow">PROJECTS // 1 ALLOCATED</p>
      <h2>What we've shipped.</h2>
    </div>
  </div>

  <div class="project-grid">

    <a class="card shipped" href="https://github.com/arelas/Phat32" target="_blank" rel="noopener">
      <div class="card-top">
        <img class="card-icon" src="/assets/phat32-icon.png" alt="">
        <span class="card-title">PHAT32</span>
      </div>
      <div class="tags">
        <span class="tag">WINDOWS</span>
        <span class="tag">WPF</span>
        <span class="tag">C#</span>
        <span class="tag">CLI</span>
      </div>
      <p class="card-desc">Formats drives as FAT32 past Windows' artificial 32&nbsp;GB limit. GUI or CLI, quick or full format with a bad-sector scan, x64 or ARM64.</p>
      <span class="card-link">View on GitHub &#8599;</span>
    </a>

    <div class="card empty">
      <span class="marker">0x00000000 // FREE</span>
      <div>
        <p class="empty-label">[ cluster free ]</p>
        <p class="empty-sub">Next project goes here. Allocated on first use.</p>
      </div>
    </div>

    <div class="card empty">
      <span class="marker">0x00000000 // FREE</span>
      <div>
        <p class="empty-label">[ cluster free ]</p>
        <p class="empty-sub">Reserved, not assigned yet.</p>
      </div>
    </div>

  </div>
</section>
""" + blog_preview_section
    html = page_shell(
        title=SITE_NAME,
        description="Whatever we build that turns out useful, we share with the world.",
        body_html=body,
        active="",
        canonical="/",
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print("  index.html")


def _sector_grid_cells():
    cols, rows = 24, 6
    total = cols * rows
    bad_indices = {17, 58, 89, 121}
    cells = []
    for i in range(total):
        if i in bad_indices:
            cells.append('      <span class="cell bad" data-tip="0x0FFFFFF7 BAD_CLUSTER"></span>')
        else:
            cells.append('      <span class="cell"></span>')
    return cells


# ---- Main -------------------------------------------------------------------

def main():
    post_paths = sorted(POSTS_DIR.glob("*.md"))
    posts = [parse_post(p) for p in post_paths]
    posts.sort(key=lambda p: p["date"], reverse=True)

    print("Building Bad Cluster site...")
    build_home(posts)
    for post in posts:
        build_post_page(post)
    build_blog_index(posts)
    build_contact_page()
    print(f"Done. {len(posts)} post(s).")

    if "YOUR_FORM_ID" in FORM_ACTION:
        print("\nNOTE: contact form still points at a placeholder Formspree ID.")
        print("      Create a form at https://formspree.io and update FORM_ACTION in build.py.")


if __name__ == "__main__":
    main()
