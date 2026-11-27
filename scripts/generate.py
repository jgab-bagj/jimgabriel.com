#!/usr/bin/env python3
"""
Static site generator for www.jimgabriel.com.

Reads data/apps.json and generates:
  - index.html
  - <app-slug>/index.html for every app in data/apps.json
  - 404.html
  - sitemap.xml
  - robots.txt

Zero external dependencies — runs with built-in macOS python3:
  python3 scripts/generate.py
"""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "apps.json"

APPLE_ICON_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.33c.64-.78 1.08-1.86.96-2.94-.93.04-2.06.62-2.72 1.4-.58.68-1.1 1.79-.96 2.84 1.04.08 2.09-.52 2.72-1.3z"/>'
    "</svg>"
)

PLAY_ICON_SVG = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M3.61 1.814L13.793 12 3.61 22.186a1.75 1.75 0 0 1-.61-1.33V3.144c0-.52.23-.99.61-1.33zM15.207 13.414l2.84 2.84-11.27 6.416 8.43-9.256zm4.19-2.385c.804.458.804 1.484 0 1.942l-1.93 1.099-2.85-2.85 2.85-2.85 1.93 1.099zM6.777 1.33l11.27 6.416-2.84 2.84-8.43-9.256z"/>'
    "</svg>"
)


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def render_head(
    *,
    title: str,
    description: str,
    canonical_url: str,
    og_image_url: str,
    prefix: str,
    json_ld: dict | None = None,
) -> str:
    json_ld_block = ""
    if json_ld:
        json_ld_block = (
            '\n  <script type="application/ld+json">\n'
            f"  {json.dumps(json_ld, ensure_ascii=False, indent=2)}\n"
            "  </script>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical_url)}">
  <link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical_url)}">
  <meta property="og:image" content="{esc(og_image_url)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og_image_url)}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/styles.css">{json_ld_block}
</head>"""


def render_header(site: dict, prefix: str, is_home: bool) -> str:
    home_href = "./" if is_home else f"{prefix}"
    apps_href = "#apps" if is_home else f"{prefix}#apps"
    ethos_href = "#philosophy" if is_home else f"{prefix}#philosophy"
    contact_href = f"mailto:{esc(site['contactEmail'])}"
    return f"""  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{home_href}">
        <span class="brand-mark" aria-hidden="true">JG</span>
        <span>{esc(site["brandName"])}</span>
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a class="nav-link" href="{apps_href}">Apps</a>
        <a class="nav-link hide-mobile" href="{ethos_href}">Philosophy</a>
        <a class="nav-link hide-mobile" href="{contact_href}">Contact</a>
        <a class="nav-cta" href="{esc(site["appStoreDeveloperUrl"])}" target="_blank" rel="noopener noreferrer">App Store ↗</a>
      </nav>
    </div>
  </header>"""


def render_footer(site: dict, apps: list[dict], prefix: str) -> str:
    year = date.today().year
    app_links = "\n".join(
        f'            <li><a href="{prefix}{esc(app["slug"])}/">{esc(app["title"])}</a></li>'
        for app in apps
    )
    play_link = ""
    if site.get("googlePlayDeveloperUrl"):
        play_link = f'\n            <li><a href="{esc(site["googlePlayDeveloperUrl"])}" target="_blank" rel="noopener noreferrer">Google Play ↗</a></li>'
    else:
        play_link = '\n            <li><span style="color: var(--text-muted); font-size: 0.9rem;">Google Play (Coming Soon)</span></li>'

    return f"""  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="brand" href="{prefix or './'}">
            <span class="brand-mark" aria-hidden="true">JG</span>
            <span>{esc(site["brandName"])}</span>
          </a>
          <p>{esc(site["tagline"])} Crafted independently with no ads, no subscriptions, and no tracking.</p>
        </div>
        <div class="footer-cols">
          <div class="footer-col">
            <h4>Games &amp; Apps</h4>
            <ul>
{app_links}
            </ul>
          </div>
          <div class="footer-col">
            <h4>Stores &amp; Contact</h4>
            <ul>
              <li><a href="{esc(site["appStoreDeveloperUrl"])}" target="_blank" rel="noopener noreferrer">Apple App Store ↗</a></li>{play_link}
              <li><a href="mailto:{esc(site["contactEmail"])}">{esc(site["contactEmail"])}</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© {year} {esc(site["developerLegalName"])}. All rights reserved.</span>
        <span>Built to be lightweight, fast, and easy to update.</span>
      </div>
    </div>
  </footer>"""


def render_android_badge(app: dict, compact: bool = False) -> str:
    android = app.get("stores", {}).get("android", {})
    status = android.get("status", "")
    url = android.get("url", "")
    if status == "live" and url:
        label = "Google Play" if compact else "Get on Google Play"
        cls = "btn btn-secondary btn-sm" if compact else "btn btn-secondary"
        return (
            f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">'
            f"{PLAY_ICON_SVG} {label}</a>"
        )
    if status == "coming-soon":
        text = "Android Soon" if compact else "Android · Coming Soon"
        return f'<span class="pill pill-android">{PLAY_ICON_SVG} {text}</span>'
    return ""


def render_home(data: dict) -> str:
    site = data["site"]
    apps = data["apps"]
    domain = site["domain"].rstrip("/")

    hero_tiles = []
    for app in apps:
        plat_label = app.get("platformLabel") or " · ".join(app["platforms"])
        hero_tiles.append(
            f"""          <a class="hero-app-tile" href="./{esc(app["slug"])}/" style="--accent: {esc(app["accent"])}; --accent-rgb: {esc(app["accentRgb"])};">
            <img class="app-icon" src="./{esc(app["icon"])}" alt="{esc(app["title"])} app icon" width="84" height="84">
            <span class="hero-app-name">{esc(app["title"])}</span>
            <span class="hero-app-price">{esc(app["price"])} · {esc(plat_label)}</span>
          </a>"""
        )

    cards = []
    for idx, app in enumerate(apps):
        platforms_html = "\n".join(
            f'              <span class="platform-chip">{esc(p)}</span>'
            for p in app["platforms"]
        )
        android_pill = ""
        if app.get("stores", {}).get("android", {}).get("status") == "coming-soon":
            android_pill = '<span class="pill pill-android">Android Soon</span>'
        elif app.get("stores", {}).get("android", {}).get("status") == "live":
            android_pill = '<span class="pill pill-live">Android Live</span>'

        status_pill = (
            '<span class="pill pill-live">Live on App Store</span>'
            if app.get("status") == "live"
            else '<span class="pill">Coming Soon</span>'
        )
        trailer_chip = (
            '              <span class="platform-chip" style="border-color: rgba(var(--accent-rgb), 0.4); color: var(--text);">▶ Trailer</span>\n'
            if app.get("trailer")
            else ""
        )
        fetch_prio = ' fetchpriority="high"' if idx == 0 else ' loading="lazy"'

        cards.append(
            f"""        <article class="app-card" data-orientation="{esc(app.get("screenshotOrientation", "landscape"))}" style="--accent: {esc(app["accent"])}; --accent-2: {esc(app["accentSecondary"])}; --accent-rgb: {esc(app["accentRgb"])};">
          <a class="app-card-media" href="./{esc(app["slug"])}/" aria-label="Explore {esc(app["title"])}">
            <div class="app-card-badges">
              {status_pill}
              {android_pill}
            </div>
            <img src="./{esc(app["heroImage"])}" alt="{esc(app["title"])} preview"{fetch_prio}>
          </a>
          <div class="app-card-body">
            <div class="app-card-head">
              <img class="app-icon" src="./{esc(app["icon"])}" alt="{esc(app["title"])} icon" width="68" height="68" loading="lazy">
              <div class="app-card-titles">
                <div class="app-card-category">{esc(app["category"])}</div>
                <h3 class="app-card-title"><a href="./{esc(app["slug"])}/">{esc(app["title"])}</a></h3>
              </div>
            </div>
            <p class="app-card-desc">{esc(app["shortDescription"])}</p>
            <div class="app-card-meta">
{platforms_html}
{trailer_chip}              <span class="price-chip">{esc(app["price"])}</span>
            </div>
            <div class="app-card-actions">
              <a class="btn btn-accent btn-sm" href="./{esc(app["slug"])}/">Explore App →</a>
              <a class="btn btn-secondary btn-sm" href="{esc(app["stores"]["ios"])}" target="_blank" rel="noopener noreferrer" aria-label="Download {esc(app["title"])} on the App Store">{APPLE_ICON_SVG} App Store</a>
            </div>
          </div>
        </article>"""
        )

    pillars = []
    for i, pillar in enumerate(site.get("pillars", []), 1):
        pillars.append(
            f"""        <div class="pillar-card">
          <span class="pillar-num">0{i}</span>
          <h3>{esc(pillar["title"])}</h3>
          <p>{esc(pillar["description"])}</p>
        </div>"""
        )

    og_image = f"{domain}/{apps[0]['heroImage']}" if apps else f"{domain}/assets/favicon.svg"
    head = render_head(
        title=f'{site["brandName"]} — Indie Games & Apps',
        description=site["heroDescription"],
        canonical_url=f"{domain}/",
        og_image_url=og_image,
        prefix="./",
        json_ld={
            "@context": "https://schema.org",
            "@type": "Person",
            "name": site["developerLegalName"],
            "alternateName": site["brandName"],
            "url": f"{domain}/",
            "sameAs": [site["appStoreDeveloperUrl"]],
        },
    )

    return f"""{head}
<body>
{render_header(site, "./", is_home=True)}

  <main id="main">
    <section class="hero">
      <div class="container hero-grid">
        <div>
          <div class="eyebrow">
            <span class="eyebrow-dot" aria-hidden="true"></span>
            <span>Independent Games &amp; Interactive Apps</span>
          </div>
          <h1 class="hero-title">{esc(site["tagline"])}</h1>
          <p class="hero-subtitle">{esc(site["heroDescription"])}</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="#apps">Browse Catalog</a>
            <a class="btn btn-secondary" href="{esc(site["appStoreDeveloperUrl"])}" target="_blank" rel="noopener noreferrer">{APPLE_ICON_SVG} View on App Store</a>
          </div>
          <div class="hero-meta-strip">
            <span class="pill">$0.99 One-Time</span>
            <span class="pill">Zero Ads</span>
            <span class="pill">Zero Tracking</span>
            <span class="pill">Works Offline</span>
          </div>
        </div>

        <div class="hero-showcase" aria-label="Featured live apps">
{chr(10).join(hero_tiles)}
        </div>
      </div>
    </section>

    <section class="section" id="apps">
      <div class="container">
        <div class="section-header">
          <div>
            <p class="section-kicker">Catalog</p>
            <h2 class="section-title">Released Games &amp; Apps</h2>
            <p class="section-desc">Each app has its own dedicated page with full screenshots, feature breakdown, and support details.</p>
          </div>
          <span class="pill pill-live">{len(apps)} Live on App Store</span>
        </div>

        <div class="apps-grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="android-banner">
          <div>
            <span class="pill pill-android">{PLAY_ICON_SVG} Expanding to Android</span>
            <h3>Android Releases Coming Soon</h3>
            <p>{esc(site["androidStatusBanner"])}</p>
          </div>
          <a class="btn btn-secondary" href="mailto:{esc(site["contactEmail"])}?subject=Android%20Release%20Updates">Get in Touch →</a>
        </div>
      </div>
    </section>

    <section class="section" id="philosophy">
      <div class="container">
        <div class="section-header">
          <div>
            <p class="section-kicker">Philosophy</p>
            <h2 class="section-title">Small-Batch Indie Software</h2>
            <p class="section-desc">Built solo with care for tactile polish, honest pricing, and respect for your privacy.</p>
          </div>
        </div>
        <div class="pillars-grid">
{chr(10).join(pillars)}
        </div>
      </div>
    </section>
  </main>

{render_footer(site, apps, "./")}
</body>
</html>
"""


def render_app_page(data: dict, app: dict) -> str:
    site = data["site"]
    apps = data["apps"]
    domain = site["domain"].rstrip("/")
    canonical = f'{domain}/{app["slug"]}/'
    og_image = f'{domain}/{app["heroImage"]}'
    orientation = app.get("screenshotOrientation", "landscape")
    is_portrait = orientation == "portrait"

    platform_pills = "\n".join(
        f'              <span class="pill">{esc(p)}</span>' for p in app["platforms"]
    )
    android_badge = render_android_badge(app, compact=False)

    trailer = app.get("trailer")
    trailer_btn_html = ""
    trailer_section_html = ""
    if trailer and trailer.get("src"):
        trailer_btn_html = '\n              <a class="btn btn-secondary" href="#trailer">▶ Watch Trailer</a>'
        poster_attr = f' poster="../{esc(trailer["poster"])}"' if trailer.get("poster") else ""
        trailer_section_html = f"""
    <section class="section" id="trailer">
      <div class="container">
        <div class="section-header">
          <div>
            <p class="section-kicker">Video</p>
            <h2 class="section-title">{esc(trailer.get("title", "Official Trailer"))}</h2>
            <p class="section-desc">{esc(trailer.get("caption", ""))}</p>
          </div>
        </div>
        <div class="trailer-frame">
          <video class="trailer-video" controls playsinline preload="metadata"{poster_attr}>
            <source src="../{esc(trailer["src"])}" type="video/mp4">
            Your browser does not support HTML5 video.
          </video>
          <div class="trailer-bar">
            <span>{esc(app["title"])} — {esc(trailer.get("title", "Official Trailer"))}</span>
            <a class="btn btn-secondary btn-sm" href="{esc(app["stores"]["ios"])}" target="_blank" rel="noopener noreferrer">{APPLE_ICON_SVG} Get on App Store ({esc(app["price"])})</a>
          </div>
        </div>
      </div>
    </section>
"""

    gallery_items = []
    for idx, shot in enumerate(app.get("screenshots", [])):
        gallery_items.append(
            f"""          <button
            type="button"
            class="gallery-item"
            data-lightbox-index="{idx}"
            data-src="../{esc(shot["src"])}"
            data-alt="{esc(shot["alt"])}"
            data-caption="{esc(shot["caption"])}"
            aria-label="Open full-size screenshot: {esc(shot["caption"])}">
            <img src="../{esc(shot["src"])}" alt="{esc(shot["alt"])}" loading="lazy">
            <span class="gallery-caption">{esc(shot["caption"])}</span>
          </button>"""
        )

    body_paragraphs = "\n".join(
        f'            <p class="story-body">{esc(p)}</p>'
        for p in app.get("bodyParagraphs", [])
    )

    feature_cards = "\n".join(
        f"""            <div class="feature-card">
              <h3>{esc(f["title"])}</h3>
              <p>{esc(f["description"])}</p>
            </div>"""
        for f in app.get("features", [])
    )

    notices_html = ""
    if app.get("notices"):
        notice_items = "\n".join(
            f"""            <div class="notice-box">
              <strong>{esc(n["title"])}</strong>
              {esc(n["text"])}
            </div>"""
            for n in app["notices"]
        )
        notices_html = f'\n          <div class="notices-stack">\n{notice_items}\n          </div>'

    highlights_html = "\n".join(
        f'              <li>{esc(item)}</li>' for item in app.get("highlights", [])
    )

    faq_items = "\n".join(
        f"""          <details class="faq-item" name="faq"{' open' if i == 0 else ''}>
            <summary>{esc(item["q"])}</summary>
            <div class="faq-answer">{esc(item["a"])}</div>
          </details>"""
        for i, item in enumerate(app.get("faq", []))
    )

    other_apps = [other for other in apps if other["slug"] != app["slug"]]
    more_cards = "\n".join(
        f"""        <a class="more-app-card" href="../{esc(other["slug"])}/" style="--accent: {esc(other["accent"])}; --accent-rgb: {esc(other["accentRgb"])};">
          <img class="app-icon app-icon-sm" src="../{esc(other["icon"])}" alt="{esc(other["title"])} icon" width="56" height="56" loading="lazy">
          <div>
            <h3>{esc(other["title"])}</h3>
            <p>{esc(other["subtitle"])}</p>
          </div>
        </a>"""
        for other in other_apps
    )

    android_spec = (
        "Live on Google Play"
        if app.get("stores", {}).get("android", {}).get("status") == "live"
        else "Coming Soon"
    )

    json_ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": app["title"],
        "description": app["shortDescription"],
        "applicationCategory": app["category"],
        "operatingSystem": app["minOs"],
        "url": canonical,
        "downloadUrl": app["stores"]["ios"],
        "image": og_image,
        "author": {
            "@type": "Person",
            "name": site["developerLegalName"],
            "url": f"{domain}/",
        },
        "offers": {
            "@type": "Offer",
            "price": app["price"].replace("$", ""),
            "priceCurrency": "USD",
        },
    }

    head = render_head(
        title=f'{app["title"]} — {site["brandName"]}',
        description=app["shortDescription"],
        canonical_url=canonical,
        og_image_url=og_image,
        prefix="../",
        json_ld=json_ld,
    )

    body_style = (
        f'--accent: {esc(app["accent"])}; '
        f'--accent-2: {esc(app["accentSecondary"])}; '
        f'--accent-rgb: {esc(app["accentRgb"])};'
    )

    return f"""{head}
<body class="app-page" style="{body_style}">
{render_header(site, "../", is_home=False)}

  <main id="main">
    <section class="app-hero">
      <div class="container">
        <a class="breadcrumb" href="../">← All Games &amp; Apps</a>

        <div class="app-hero-grid">
          <div>
            <div class="app-hero-identity">
              <img class="app-icon app-icon-lg" src="../{esc(app["icon"])}" alt="{esc(app["title"])} app icon" width="96" height="96">
              <div>
                <div class="app-card-category">{esc(app["category"])}</div>
                <h1 class="app-hero-title">{esc(app["title"])}</h1>
              </div>
            </div>

            <p class="app-hero-subtitle">{esc(app["subtitle"])}</p>

            <div class="app-hero-pills">
              <span class="pill pill-live">Live on App Store</span>
{platform_pills}
              <span class="pill pill-accent">{esc(app["price"])}</span>
            </div>

            <div class="app-hero-actions">
              <a class="btn btn-accent" href="{esc(app["stores"]["ios"])}" target="_blank" rel="noopener noreferrer">{APPLE_ICON_SVG} Download on App Store</a>{trailer_btn_html}
              {android_badge}
            </div>

            <p class="app-pricing-note">{esc(app["pricingNote"])}</p>
          </div>

          <div class="app-hero-visual{' is-portrait' if is_portrait else ''}">
            <img src="../{esc(app["heroImage"])}" alt="{esc(app["title"])} hero showcase" fetchpriority="high">
          </div>
        </div>
      </div>
    </section>
{trailer_section_html}
    <section class="section" id="screenshots">
      <div class="container">
        <div class="section-header">
          <div>
            <p class="section-kicker">Gallery</p>
            <h2 class="section-title">Screenshots</h2>
            <p class="section-desc">Click any screenshot to inspect full-size.</p>
          </div>
          <div class="gallery-controls" aria-label="Gallery navigation">
            <button type="button" class="gallery-btn" data-gallery-prev aria-label="Scroll screenshots left">←</button>
            <button type="button" class="gallery-btn" data-gallery-next aria-label="Scroll screenshots right">→</button>
          </div>
        </div>

        <div class="gallery-track is-{esc(orientation)}" data-gallery-track>
{chr(10).join(gallery_items)}
        </div>
      </div>
    </section>

    <section class="section" id="features">
      <div class="container details-layout">
        <div>
          <p class="section-kicker">Overview</p>
          <h2 class="section-title" style="margin-bottom: 1.25rem;">Inside {esc(app["title"])}</h2>
          <p class="story-lead">{esc(app["leadParagraph"])}</p>
{body_paragraphs}

          <div class="features-grid">
{feature_cards}
          </div>{notices_html}
        </div>

        <aside class="specs-card" aria-label="App details">
          <h3>App Details</h3>
          <dl class="specs-list">
            <div class="spec-row"><dt>Price</dt><dd>{esc(app["price"])} (One-time)</dd></div>
            <div class="spec-row"><dt>Platforms</dt><dd>{esc(", ".join(app["platforms"]))}</dd></div>
            <div class="spec-row"><dt>Android</dt><dd>{esc(android_spec)}</dd></div>
            <div class="spec-row"><dt>Requires</dt><dd>{esc(app["minOs"])}</dd></div>
            <div class="spec-row"><dt>Age Rating</dt><dd>{esc(app["rating"])}</dd></div>
            <div class="spec-row"><dt>Version</dt><dd>{esc(app["version"])}</dd></div>
            <div class="spec-row"><dt>Released</dt><dd>{esc(app["releaseDate"])}</dd></div>
            <div class="spec-row"><dt>Plays Offline</dt><dd>{"Yes" if app.get("offline") else "No"}</dd></div>
          </dl>
          <ul class="highlights-list">
{highlights_html}
          </ul>
        </aside>
      </div>
    </section>

    <section class="section" id="support">
      <div class="container">
        <div class="section-header">
          <div>
            <p class="section-kicker">Support &amp; Privacy</p>
            <h2 class="section-title">Questions &amp; Help</h2>
          </div>
        </div>

        <div class="support-grid">
          <div class="faq-list">
{faq_items}
          </div>

          <div class="support-card">
            <div>
              <h3>Need Help or Found a Bug?</h3>
              <p>Email <strong>{esc(site["contactEmail"])}</strong> with your device model, OS version, and what happened. Screenshots are always helpful.</p>
              <div style="margin-top: 1rem;">
                <a class="btn btn-secondary btn-sm" href="mailto:{esc(site["contactEmail"])}?subject={esc(app["title"].replace(' ', '%20'))}%20Support">Email Support ↗</a>
              </div>
            </div>
            <hr class="divider">
            <div id="privacy">
              <h3>Privacy Policy</h3>
              <p>{esc(app["privacySummary"])}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-header">
          <div>
            <p class="section-kicker">More by {esc(site["brandName"])}</p>
            <h2 class="section-title">Explore Other Releases</h2>
          </div>
          <a class="btn btn-secondary btn-sm" href="../">View All Apps</a>
        </div>
        <div class="more-apps-grid">
{more_cards}
        </div>
      </div>
    </section>
  </main>

  <dialog id="screenshot-lightbox" class="lightbox" closedby="any" aria-label="Screenshot viewer">
    <div class="lightbox-shell">
      <div class="lightbox-bar">
        <span class="lightbox-counter" data-lightbox-counter>1 / {len(app.get("screenshots", []))}</span>
        <div class="lightbox-actions">
          <button type="button" class="lightbox-btn" data-lightbox-prev aria-label="Previous screenshot">←</button>
          <button type="button" class="lightbox-btn" data-lightbox-next aria-label="Next screenshot">→</button>
          <button type="button" class="lightbox-btn" data-lightbox-close aria-label="Close viewer">✕</button>
        </div>
      </div>
      <div class="lightbox-stage">
        <img src="" alt="" data-lightbox-img>
      </div>
      <p class="lightbox-caption" data-lightbox-caption></p>
    </div>
  </dialog>

{render_footer(site, apps, "../")}
  <script src="../js/main.js" defer></script>
</body>
</html>
"""


def render_404(data: dict) -> str:
    site = data["site"]
    apps = data["apps"]
    domain = site["domain"].rstrip("/")
    head = render_head(
        title=f'Page Not Found — {site["brandName"]}',
        description="The page you were looking for could not be found.",
        canonical_url=f"{domain}/404.html",
        og_image_url=f"{domain}/assets/favicon.svg",
        prefix="/",
    )
    return f"""{head}
<body>
{render_header(site, "/", is_home=False)}
  <main id="main" class="section" style="padding: 6rem 0;">
    <div class="container" style="text-align: center; max-width: 560px;">
      <p class="section-kicker">404</p>
      <h1 class="section-title" style="margin-bottom: 1rem;">Page Not Found</h1>
      <p class="hero-subtitle" style="margin-inline: auto;">That route doesn't exist — head back to the catalog to browse all games and apps.</p>
      <a class="btn btn-primary" href="/">← Back to Portfolio</a>
    </div>
  </main>
{render_footer(site, apps, "/")}
</body>
</html>
"""


def render_sitemap(data: dict) -> str:
    domain = data["site"]["domain"].rstrip("/")
    today = date.today().isoformat()
    urls = [f"{domain}/"] + [f'{domain}/{app["slug"]}/' for app in data["apps"]]
    entries = "\n".join(
        f"  <url>\n    <loc>{esc(url)}</loc>\n    <lastmod>{today}</lastmod>\n  </url>"
        for url in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    # Generate homepage
    (ROOT / "index.html").write_text(render_home(data), encoding="utf-8")
    print("Generated index.html")

    # Generate dedicated page per app
    for app in data["apps"]:
        slug = app["slug"]
        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(render_app_page(data, app), encoding="utf-8")
        print(f"Generated {slug}/index.html")

    # Generate 404, sitemap, robots.txt
    (ROOT / "404.html").write_text(render_404(data), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(data), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f'User-agent: *\nAllow: /\nSitemap: {data["site"]["domain"].rstrip("/")}/sitemap.xml\n',
        encoding="utf-8",
    )
    print("Generated 404.html, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
