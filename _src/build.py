#!/usr/bin/env python3
"""Build dnnr.us static pages from _src/ into the repo root.

    python3 _src/build.py

Inputs:  _src/apps.json (app registry), _src/content/*.html (long-form copy)
Outputs: index.html, services.html, apps.html, contact.html, privacy-policy.html,
         support.html, delete-account.html, ko/{privacy-policy,support,delete-account}.html
         (Korean, reachable only by URL), academic_cv_support.html, 404.html,
         sitemap.xml, robots.txt

The repo root is served as-is by Cloudflare Pages (dnnr.us) and GitHub Pages
(dnnr.mrsap.com), so generated files are committed. Do not hand-edit them.
The contact form posts to functions/api/contact.js (Cloudflare Pages Function → Telegram).
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://dnnr.us"
EMAIL = "hello@dnnr.us"
CITY = "San Jose, California"
YEAR = date.today().year

REG = json.loads((SRC / "apps.json").read_text())
APPS = REG["apps"]
BY_SLUG = {a["slug"]: a for a in APPS}
CATS = {c["id"]: c["label"] for c in REG["categories"]}

e = html.escape


def asset_version(rel):
    """Short content hash so /static/* (cached for a day via _headers) is refetched after each change."""
    import hashlib
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:10]


CSS_V = asset_version("static/site.css")
JS_V = asset_version("static/site.js")
HERO_V = asset_version("static/hero.js")

# ---------------------------------------------------------------- icons

APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.37 12.64c-.02-2.24 1.83-3.32 1.91-3.37-1.04-1.52-2.66-1.73-3.24-1.75-1.38-.14-2.69.81-3.39.81-.7 0-1.78-.79-2.92-.77-1.5.02-2.89.87-3.66 2.22-1.56 2.71-.4 6.72 1.12 8.91.74 1.07 1.63 2.28 2.8 2.23 1.12-.04 1.55-.73 2.9-.73 1.36 0 1.74.73 2.93.71 1.21-.02 1.98-1.09 2.72-2.17.86-1.25 1.21-2.46 1.23-2.52-.03-.01-2.36-.9-2.4-3.57zM14.14 6.07c.62-.75 1.04-1.8.92-2.84-.89.04-1.97.59-2.61 1.34-.57.66-1.07 1.73-.94 2.75.99.08 2.01-.5 2.63-1.25z"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.6 2.3c-.3.3-.4.7-.4 1.2v17c0 .5.1.9.4 1.2l9.4-9.7L4.6 2.3zm10.8 11.1 2.8 2.9-11.6 6.6c-.4.2-.8.3-1.1.2l9.9-9.7zm4.4-3.6c.7.4 1 .9 1 1.4s-.3 1.1-1 1.4l-2.5 1.4-3-3.1 3-3.1 2.5 2zM6.6 1.1l11.6 6.6-2.8 2.9-9.9-9.7c.3-.1.7 0 1.1.2z"/></svg>'

_PATHS = {
    "sparkle": '<path d="M12 3.5l1.9 5.1 5.1 1.9-5.1 1.9L12 17.5l-1.9-5.1L5 10.5l5.1-1.9L12 3.5Z"/><path d="M18.5 15.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7.7-1.8Z"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "text": '<path d="M4 6h16M4 10h11M4 14h16M4 18h8"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "translate": '<path d="M4 5h9M8.5 3v2M6 5c.5 3 2.5 5.5 5 7M11 5c-.8 3.5-3 6.5-6.5 8"/><path d="m13 21 4-9 4 9M14.5 17.5h5"/>',
    "shield": '<path d="M12 3 5 6v5c0 4.5 3 8.5 7 10 4-1.5 7-5.5 7-10V6l-7-3Z"/><path d="m9 12 2 2 4-4"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2.5v3.5M15 2.5v3.5M9 18v3.5M15 18v3.5M2.5 9H6M2.5 15H6M18 9h3.5M18 15h3.5"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "cloud": '<path d="M7 18h10a4 4 0 0 0 .6-7.95A6 6 0 0 0 6.2 9.4 4.3 4.3 0 0 0 7 18Z"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "message": '<path d="M4 5h16v11H9l-5 4V5Z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M12 21s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.5 3.3-5.5 6.5-5.5s5.7 2 6.5 5.5"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20c-.5-2.6-2-4.4-4-5.1"/>',
    "rocket": '<path d="M5 15c-1.5 1.5-2 4-2 6 2 0 4.5-.5 6-2"/><path d="M9 15l-3-3c1.5-4.5 5-8.5 12-9-.5 7-4.5 10.5-9 12Z"/><circle cx="14.5" cy="9.5" r="1.5"/>',
}


def icon(name, cls="gi"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{_PATHS[name]}</svg>'


ARROW = '<span class="arrow" aria-hidden="true">→</span>'

SVG_DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="brandStroke" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3BA6E8"/><stop offset=".38" stop-color="#8B6CE0"/><stop offset=".62" stop-color="#8CCB4F"/><stop offset=".85" stop-color="#F57FA0"/><stop offset="1" stop-color="#F7A26B"/>
    </linearGradient>
    <linearGradient id="brandFill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3BA6E8"/><stop offset=".5" stop-color="#8B6CE0"/><stop offset="1" stop-color="#F57FA0"/>
    </linearGradient>
  </defs>
</svg>"""


def ai_badge(a):
    return f'<span class="ai-badge" title="AI feature">{icon("sparkle")}{e(a["ai"])}</span>' if a.get("ai") else ""


def ios_url(a):
    return f"https://apps.apple.com/app/id{a['ios_id']}"


def play_url(a):
    return f"https://play.google.com/store/apps/details?id={a['android_id']}"


def contact_btn(label, source, topic="", cls="btn btn-ink", with_arrow=False):
    t = f' data-topic="{e(topic)}"' if topic else ""
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="/contact" data-contact data-source="{source}" data-label="{e(label)}"{t}>{e(label)}{ARROW if with_arrow else ""}</a>'


# ---------------------------------------------------------------- contact form

TOPICS = ["Consulting inquiry", "Partnership", "App support", "Privacy request", "Data deletion request", "Other"]


def contact_form(source, topic=TOPICS[0], idp="cf"):
    opts = "".join(f'<option{" selected" if t == topic else ""}>{e(t)}</option>' for t in TOPICS)
    return f"""
<form class="form contact-form" data-source="{source}" novalidate>
  <div class="row">
    <div class="field"><label for="{idp}-name">Name</label><input id="{idp}-name" name="name" autocomplete="name" maxlength="100" required><span class="err" aria-live="polite"></span></div>
    <div class="field"><label for="{idp}-email">Email</label><input id="{idp}-email" name="email" type="email" autocomplete="email" maxlength="200" required placeholder="you@company.com"><span class="err" aria-live="polite"></span></div>
  </div>
  <div class="row">
    <div class="field"><label for="{idp}-company">Company <span class="opt">(optional)</span></label><input id="{idp}-company" name="company" autocomplete="organization" maxlength="120"></div>
    <div class="field"><label for="{idp}-topic">Topic</label><select id="{idp}-topic" name="topic">{opts}</select></div>
  </div>
  <div class="field"><label for="{idp}-message">How can we help?</label><textarea id="{idp}-message" name="message" maxlength="4000" required placeholder="Tell us about your product, stage, and timeline."></textarea><span class="err" aria-live="polite"></span></div>
  <div class="hp" aria-hidden="true"><label for="{idp}-website">Website</label><input id="{idp}-website" name="website" tabindex="-1" autocomplete="off"></div>
  <div class="foot">
    <p class="note">We use your details only to reply to you. See our <a href="/privacy-policy">Privacy Policy</a>.</p>
    <button class="btn btn-ink" type="submit">Send message</button>
  </div>
  <p class="status" role="alert"></p>
</form>
<div class="form-done" hidden>
  <div class="ok">{icon("check")}</div>
  <h3>Thanks, your message is on its way.</h3>
  <p>We'll reply to the email you provided, usually within a few business days.</p>
</div>"""


CONTACT_DIALOG = f"""
<dialog class="modal" id="contact-dialog" aria-labelledby="contact-title">
  <div class="mhead">
    <div><h2 id="contact-title">Get in touch</h2><p>Tell us what you're working on. We'll get back to you by email.</p></div>
    <button class="close" type="button" data-close aria-label="Close">×</button>
  </div>
  <div class="mbody">{contact_form("dialog", idp="dlg")}</div>
</dialog>"""


# ---------------------------------------------------------------- layout

def layout(*, path, title, description, body, current="", head_extra="", lang="en", dialog=True):
    canonical = SITE + (path if path != "/index" else "/")
    full_title = title if title.startswith("DNNR Tech") else f"{title} — DNNR Tech"
    cur = ' aria-current="page"'
    nav = [("/services", "Services", "services", ""), ("/apps", "Apps", "apps", ""), ("/support", "Support", "support", "hide-sm")]
    nav_html = "".join(f'<a class="{c}" href="{h}"{cur if k == current else ""}>{l}</a>' for h, l, k, c in nav)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#FAFAFB" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0A0A0F" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DNNR Tech">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/static/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/static/favicon-32.png">
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/static/site.css?v={CSS_V}">
<script src="/static/site.js?v={JS_V}" defer></script>
{head_extra}
</head>
<body>
{SVG_DEFS}
<header class="site-header">
  <div class="container bar">
    <a class="brand" href="/" aria-label="DNNR Tech home"><img src="/static/dnnr-mark.png" alt="" width="34" height="19">DNNR Tech</a>
    <nav class="nav" aria-label="Primary">{nav_html}{contact_btn("Contact", "nav_contact", cls="btn btn-ink btn-sm")}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="container">
    <div class="foot">
      <div class="about">
        <a class="brand" href="/"><img src="/static/dnnr-mark.png" alt="" width="34" height="19">DNNR Tech</a>
        <p>Daily needs, naturally refined. AI products and startup consulting from {CITY}.</p>
      </div>
      <div><b>Company</b><a href="/services">Services</a><a href="/apps">Apps</a><a href="/contact" data-contact data-source="footer_contact">Contact</a></div>
      <div><b>Help</b><a href="/support">Support</a><a href="/delete-account">Data deletion</a></div>
      <div><b>Legal</b><a href="/privacy-policy">Privacy Policy</a></div>
    </div>
    <div class="copyright"><span>© {YEAR} DNNR Tech. All rights reserved.</span><span>Our apps are independent and not affiliated with the brands they reference.</span></div>
  </div>
</footer>
{CONTACT_DIALOG if dialog else ""}
</body>
</html>
"""


def content(name):
    return (SRC / "content" / name).read_text()


def toc_from(html_text):
    return re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', html_text)


def doc_page(*, path, title, description, eyebrow, heading, meta="", body_html, toc=None, current="", lang="en"):
    toc_html = ""
    if toc:
        label = "목차" if lang == "ko" else "On this page"
        toc_html = f'<nav class="toc" aria-label="{label}"><b>{label}</b>' + "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in toc) + "</nav>"
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>{e(eyebrow)}</span>
    <h1>{heading}</h1>
    <p class="meta">{meta}</p>
  </div>
  <div class="{'doc-layout' if toc else 'doc-layout single'}">
    {toc_html}
    <article class="prose" lang="{lang}">{body_html}</article>
  </div>
</div>"""
    return layout(path=path, title=title, description=description, body=body, current=current, lang=lang)


# ---------------------------------------------------------------- art

AI_TICKER = ["Generative AI", "Large language models", "Multimodal AI", "Computer vision", "AI agents", "RAG",
             "Semantic search", "Vector embeddings", "Speech AI", "On-device ML", "AI data pipelines", "AI trust & safety"]

# Particle scene (static/hero.js): grey particles drift ("daily needs"), rush in and take the logo's colors
# to form the DNNR mark ("naturally refined"), hold, then burst. Ticker lists the AI we build with.
HERO_ART = f"""
<div class="hero-art pc-scene" data-logo="/static/dnnr-mark-lg.png" data-phase="drift" aria-hidden="true">
  <canvas></canvas>
  <span class="pc-cap a">Daily needs</span>
  <span class="pc-cap b">Naturally refined</span>
  <div class="pc-ticker"><div class="track">{''.join(f'<span>{e(t)}</span>' for t in AI_TICKER * 2)}</div></div>
</div>"""

ART_PRODUCTS = """
<svg viewBox="0 0 560 230" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <rect class="art-fill" x="318" y="46" width="118" height="222" rx="22" opacity=".8"/>
  <rect class="art-bar" x="334" y="80" width="86" height="10" rx="5"/>
  <rect class="art-bar" x="334" y="100" width="60" height="10" rx="5"/>
  <rect class="art-fill" x="206" y="26" width="132" height="244" rx="24"/>
  <rect class="art-bar" x="224" y="48" width="44" height="8" rx="4"/>
  <rect class="art-grad" x="222" y="68" width="100" height="72" rx="14" opacity=".9"/>
  <path d="M272 90l3.2 8.6 8.6 3.2-8.6 3.2-3.2 8.6-3.2-8.6-8.6-3.2 8.6-3.2 3.2-8.6Z" fill="#fff" opacity=".95"/>
  <rect class="art-bar" x="222" y="154" width="100" height="10" rx="5"/>
  <rect class="art-bar" x="222" y="172" width="76" height="10" rx="5"/>
  <rect class="art-bar" x="222" y="190" width="88" height="10" rx="5"/>
  <rect class="art-fill" x="112" y="70" width="104" height="54" rx="14"/>
  <circle cx="134" cy="97" r="10" fill="url(#brandFill)" opacity=".85"/>
  <rect class="art-bar" x="152" y="88" width="50" height="7" rx="3.5"/>
  <rect class="art-bar" x="152" y="101" width="34" height="7" rx="3.5"/>
</svg>"""

ART_CONSULTING = """
<svg viewBox="0 0 560 230" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <path class="art-path" d="M70 178 C 170 178, 190 118, 280 118 S 400 70, 492 62"/>
  <g><circle class="art-node" cx="84" cy="178" r="9"/><text class="art-text" x="84" y="207" text-anchor="middle">Idea</text></g>
  <g><circle class="art-node" cx="280" cy="118" r="9"/><text class="art-text" x="280" y="147" text-anchor="middle">MVP</text></g>
  <g><circle cx="488" cy="63" r="12" fill="url(#brandFill)"/><text class="art-text" x="488" y="95" text-anchor="middle">Launch</text></g>
  <rect class="art-fill" x="120" y="48" width="120" height="44" rx="12"/>
  <rect class="art-bar" x="136" y="62" width="64" height="7" rx="3.5"/>
  <rect class="art-bar" x="136" y="75" width="88" height="7" rx="3.5"/>
  <rect class="art-fill" x="330" y="150" width="136" height="44" rx="12"/>
  <circle cx="352" cy="172" r="8" fill="url(#brandFill)" opacity=".85"/>
  <rect class="art-bar" x="368" y="164" width="80" height="7" rx="3.5"/>
  <rect class="art-bar" x="368" y="177" width="56" height="7" rx="3.5"/>
</svg>"""


ART_ROADMAP = """
<div class="hero-art roadmap" aria-hidden="true">
  <svg viewBox="0 0 520 520">
    <defs>
      <pattern id="dots2" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.1" class="art-dots"/></pattern>
      <radialGradient id="rgA" cx="20%" cy="80%" r="55%"><stop offset="0" stop-color="#3BA6E8" stop-opacity=".30"/><stop offset="1" stop-color="#3BA6E8" stop-opacity="0"/></radialGradient>
      <radialGradient id="rgB" cx="85%" cy="15%" r="55%"><stop offset="0" stop-color="#F57FA0" stop-opacity=".28"/><stop offset="1" stop-color="#F57FA0" stop-opacity="0"/></radialGradient>
      <radialGradient id="rgC" cx="55%" cy="50%" r="35%"><stop offset="0" stop-color="#8B6CE0" stop-opacity=".22"/><stop offset="1" stop-color="#8B6CE0" stop-opacity="0"/></radialGradient>
      <clipPath id="rmClip"><rect x="10" y="10" width="500" height="500" rx="44"/></clipPath>
    </defs>
    <rect class="art-frame" x="10" y="10" width="500" height="500" rx="44"/>
    <g clip-path="url(#rmClip)">
      <rect x="10" y="10" width="500" height="500" fill="url(#dots2)"/>
      <rect x="10" y="10" width="500" height="500" fill="url(#rgA)"/>
      <rect x="10" y="10" width="500" height="500" fill="url(#rgB)"/>
      <rect x="10" y="10" width="500" height="500" fill="url(#rgC)"/>
      <path class="art-path" d="M84 420 C 170 420, 150 330, 214 318 S 300 250, 318 212 S 380 120, 430 104"/>
      <g><circle class="art-node" cx="84" cy="420" r="10"/><text class="art-text" x="84" y="452" text-anchor="middle">Discovery</text></g>
      <g><circle class="art-node" cx="214" cy="318" r="10"/><text class="art-text" x="214" y="350" text-anchor="middle">Prototype</text></g>
      <g><circle class="art-node" cx="318" cy="212" r="10"/><text class="art-text" x="318" y="244" text-anchor="middle">MVP</text></g>
      <g><circle cx="430" cy="104" r="15" fill="url(#brandFill)"/><path d="M430 94l2.6 7 7 2.6-7 2.6-2.6 7-2.6-7-7-2.6 7-2.6 2.6-7Z" fill="#fff"/><text class="art-text" x="430" y="142" text-anchor="middle">Launch</text></g>
      <g transform="translate(52 64)"><rect class="art-fill" width="176" height="92" rx="16"/><rect class="art-grad" x="16" y="16" width="40" height="40" rx="11" opacity=".9"/><rect class="art-bar" x="68" y="20" width="88" height="9" rx="4.5"/><rect class="art-bar" x="68" y="38" width="60" height="9" rx="4.5"/><rect class="art-bar" x="16" y="68" width="144" height="8" rx="4"/></g>
      <g transform="translate(300 312)"><rect class="art-fill" width="172" height="100" rx="16"/><circle cx="34" cy="34" r="16" fill="url(#brandFill)" opacity=".85"/><rect class="art-bar" x="60" y="24" width="92" height="9" rx="4.5"/><rect class="art-bar" x="60" y="41" width="64" height="9" rx="4.5"/><rect class="art-bar" x="18" y="68" width="136" height="8" rx="4"/><rect class="art-bar" x="18" y="82" width="96" height="8" rx="4"/></g>
    </g>
  </svg>
  <span class="chip-float c-a" style="top:36%;left:-4%"><i>""" + icon("rocket") + """</i>Idea to launch</span>
  <span class="chip-float c-b" style="top:auto;bottom:30%;right:-4%"><i>""" + icon("sparkle") + """</i>AI-first</span>
</div>"""


# ---------------------------------------------------------------- shared content

SERVICES = [
    {
        "id": "mvp", "icon": "rocket", "slug": "ai-product-mvp-development", "related": ["what-to-eat", "snap-and-shake", "targeted-resume-ai"],
        "faq": [
            ("What is included in an MVP engagement?", "Scoping, a clickable prototype, the MVP build, testing, and launch support. We agree on the exact scope and milestones in the proposal."),
            ("Can you build AI features into the MVP?", "Yes. We design features such as vision, text generation, search, and moderation, and plan for cost and reliability from the start."),
            ("Do you work with early-stage founders?", "Yes. Many projects start from an idea and a few target users; we help turn that into a focused first version people can use."),
        ],
        "title": "AI product & MVP development",
        "summary": "Turn an idea into a launch-ready product with AI at its core, fast.",
        "tags": ["Prototype", "AI features", "MVP"],
        "points": ["Product scoping and a lean feature plan", "Clickable prototype to validate early",
                   "AI features: multimodal, generative, semantic search, trust & safety", "MVP build, testing, and launch"],
        "ideal": "Founders validating a new product idea, or teams that need a working MVP to raise or sell.",
        "deliverables": ["Product and feature spec", "Interactive prototype", "Production MVP", "Launch plan"],
    },
    {
        "id": "mobile", "icon": "phone", "slug": "mobile-app-development", "related": ["automiles", "stamprescue", "golf-passport"],
        "faq": [
            ("Do you build for both iOS and Android?", "Yes. We build production-ready apps for iPhone, iPad, and Android and launch them on the App Store and Google Play."),
            ("Can you build the backend too?", "Yes. Servers, APIs, databases, sign-in, payments, analytics, and notifications, everything the app needs to run in production."),
            ("Do you handle App Store and Google Play submission?", "Yes, including store listings, review requirements, and release management."),
        ],
        "title": "Mobile app development",
        "summary": "Native iOS and Android apps, built to production quality and launched on both stores.",
        "tags": ["iOS", "Android", "Backend", "Launch"],
        "points": ["Native apps for iPhone, iPad, and Android", "Backend servers, APIs, and databases",
                   "Sign-in, payments, analytics, and notifications", "App Store and Google Play launch"],
        "ideal": "Startups that need a production-ready app on both platforms, with the backend to run it.",
        "deliverables": ["iOS and Android apps", "Backend and admin tools", "Analytics and monetization", "Store listings and release"],
    },
    {
        "id": "ai", "icon": "sparkle", "slug": "ai-integration-advisory", "related": ["tj-near-hot", "bapmap", "swing-like-pro"],
        "faq": [
            ("Which AI models do you work with?", "We choose models for the job, weighing quality, cost, latency, and privacy, rather than tying you to a single vendor."),
            ("Can you help reduce our AI costs?", "Yes. We review model choices, prompts, caching, and architecture to lower cost and latency while keeping quality."),
            ("How do you make AI features reliable?", "With evaluation sets built from real inputs, guardrails, fallbacks, and monitoring once the feature is live."),
        ],
        "title": "AI integration advisory",
        "summary": "Bring production-grade generative and multimodal AI into your product, with cost and quality under control.",
        "tags": ["LLMs", "Vision", "Evaluation", "Cost"],
        "points": ["Where AI helps users, and where it doesn't", "Choosing the right models for the job",
                   "Prompt design, evaluation, and guardrails", "Cost, latency, and privacy architecture"],
        "ideal": "Products that want to add AI features, or teams whose AI costs and quality need a second look.",
        "deliverables": ["AI opportunity map", "Model and cost analysis", "Working prototype", "Evaluation and guardrail plan"],
    },
]

CAPABILITIES = [
    ("eye", "Multimodal AI", "Vision-language models that understand photos, documents, and the world around the user."),
    ("text", "Generative AI & LLMs", "Products that write, rewrite, and reason with large language models."),
    ("search", "Semantic search", "Vector-embedding search and discovery that understands intent, not keywords."),
    ("shield", "AI trust & safety", "LLM moderation that keeps user-generated content safe, in any language."),
    ("layers", "AI data pipelines", "Pipelines that gather, clean, and structure live real-world data at scale."),
    ("cpu", "On-device ML", "Private, low-latency models that run entirely on the phone."),
]

# Capability → app where it runs in production (all verified against the apps' code).
PROOFS = [
    ("eye", "Multimodal AI", "what-to-eat", "Vision-language AI that reads any menu from one photo and explains every dish."),
    ("text", "Generative AI", "targeted-resume-ai", "Parses a job post and rewrites a resume to match it."),
    ("search", "Semantic discovery", "tj-near-hot", "Vector-embedding search plus LLM trust & safety for a shopper community."),
    ("cpu", "On-device computer vision", "swing-like-pro", "Frame-by-frame pose tracking and 3D swing comparison, entirely on the phone."),
    ("shield", "Privacy-first on-device AI", "golf-passport", "Reconstructs every course a golfer has played from photo data, with no uploads."),
    ("layers", "AI data pipelines", "charge-and-grab", "Structures live place data around every Supercharger into instant recommendations."),
]

ORG_LD = {
    "@context": "https://schema.org", "@type": "Organization", "name": "DNNR Tech", "url": SITE,
    "logo": f"{SITE}/static/icon-512.png", "slogan": "Daily Needs, Naturally Refined",
    "description": "San Jose-based technology company building AI-powered products and providing startup product, mobile, and AI consulting.",
    "address": {"@type": "PostalAddress", "addressLocality": "San Jose", "addressRegion": "CA", "addressCountry": "US"},
    "knowsAbout": ["Artificial intelligence", "Large language models", "Computer vision", "iOS app development", "Android app development", "Backend development", "MVP development"],
    "sameAs": ["https://www.linkedin.com/company/dnnr-us/", "https://apps.apple.com/developer/id1668952055",
               "https://play.google.com/store/apps/dev?id=6001862912587595419"],
}


def section_head(kicker, title, sub="", action=""):
    return f"""<div class="section-head"><div><span class="kicker">{e(kicker)}</span><h2 class="h2">{title}</h2>{f'<p>{sub}</p>' if sub else ''}</div>{action}</div>"""


def cta(title, sub, source, label="Start a conversation"):
    return f"""
<section style="padding-top:16px">
  <div class="container">
    <div class="cta">
      <div><h2>{title}</h2><p>{sub}</p></div>
      {contact_btn(label, source, TOPICS[0], cls="btn", with_arrow=True)}
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- pages

def page_home():
    services = "".join(f"""
      <a class="service" href="/services/{sv['slug']}">
        <div class="icon-tile">{icon(sv['icon'])}</div>
        <h3>{e(sv['title'])}</h3>
        <p>{e(sv['summary'])}</p>
        <div class="tags">{''.join(f'<span class="tag">{e(t)}</span>' for t in sv['tags'])}</div>
        <span class="more">Learn more {ARROW}</span>
      </a>""" for sv in SERVICES)
    caps = "".join(f'<div><div class="icon-tile">{icon(i)}</div><b>{e(t)}</b><span>{e(d)}</span></div>' for i, t, d in CAPABILITIES)
    work = "".join(f"""
      <a class="work-card" href="/apps/{a['slug']}">
        <div class="top"><img class="icon" src="/static/apps/{a['slug']}.png" alt="{e(a['name'])} app icon" width="56" height="56" loading="lazy">{ai_badge(a)}</div>
        <h3>{e(a['name'])}</h3>
        <p>{e(a.get('ai_story') or a['tagline'])}</p>
      </a>""" for a in APPS if a.get("featured"))
    body = f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow"><span class="dot"></span>{CITY} · AI technology company</span>
      <h1 class="display motto"><span class="line"><b class="i1">D</b>aily <b class="i2">N</b>eeds,</span><span class="line"><b class="i3">N</b>aturally <b class="i4">R</b>efined.</span></h1>
      <p class="lead">DNNR Tech is a Silicon Valley technology company. We build AI-powered products for everyday life, and help startups turn ideas into products people use every day.</p>
      <div class="actions">
        {contact_btn("Start a project", "home_hero", TOPICS[0], with_arrow=True)}
        <a class="btn btn-ghost" href="/services">Our services</a>
      </div>
    </div>
    {HERO_ART}
  </div>
</section>

<section>
  <div class="container">
    {section_head("What we do", "Products and partnership,<br>from one team.", "We build and run our own AI products, and bring that same hands-on experience to founders.")}
    <div class="pillars">
      <a class="pillar" href="/apps">
        <div class="art">{ART_PRODUCTS}</div>
        <div class="content">
          <span class="kicker">Products</span>
          <h3>AI-powered apps for everyday life</h3>
          <p>We design, build, and operate consumer apps on the App Store and Google Play, from multimodal AI that reads any menu to generative AI that tailors resumes and on-device AI that turns a photo library into a travel log.</p>
          <span class="more">Explore our apps <span>→</span></span>
        </div>
      </a>
      <a class="pillar" href="/services">
        <div class="art">{ART_CONSULTING}</div>
        <div class="content">
          <span class="kicker">Consulting</span>
          <h3>From idea to launched product</h3>
          <p>We help startups scope an MVP, build and launch production-ready iOS and Android apps with the backend behind them, and add AI features that are useful, reliable, and affordable to run.</p>
          <span class="more">Our services <span>→</span></span>
        </div>
      </a>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("Capabilities", "The AI stack we ship to production.", "The same technology powers our own apps and the products we build for startups.")}
    <div class="cap-strip">{caps}</div>
  </div>
</section>

<section>
  <div class="container">
    {section_head("Consulting", "How we help startups.", "Hands-on product, mobile, and AI engineering from a team that ships its own products.", '<a class="btn btn-ghost" href="/services">All services</a>')}
    <div class="services">{services}</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("Selected work", "Built and run by us.", "A few of our AI-powered apps, live on the App Store and Google Play.", '<a class="btn btn-ghost" href="/apps">View all apps</a>')}
    <div class="work">{work}</div>
  </div>
</section>

<section>
  <div class="container editorial">
    <div class="intro">
      <span class="kicker">How we build</span>
      <h2 class="h2" style="margin-top:14px">Small teams.<br>Real products.</h2>
      <p>We keep scope tight, ship early, and let real users tell us what to build next.</p>
    </div>
    <ol class="plist">
      <li><span class="n">01</span><div><h3>Ship early, learn fast</h3><p>Small scope, real users, quick iterations. We launch, measure, and improve instead of polishing in private.</p></div></li>
      <li><span class="n">02</span><div><h3>Practical AI</h3><p>We use AI where it saves people time, and we design for cost, speed, and failure cases from day one.</p></div></li>
      <li><span class="n">03</span><div><h3>Built to operate</h3><p>Analytics, store compliance, and privacy are part of the product, not an afterthought.</p></div></li>
    </ol>
  </div>
</section>
{cta("Have an idea worth building?", "Tell us about your product. We'll get back to you within a few business days.", "home_cta")}"""
    return layout(path="/index", title="DNNR Tech — Daily Needs, Naturally Refined",
                  description="DNNR Tech is a San Jose, California technology company building AI-powered products and helping startups with product, mobile, and AI development.",
                  body=body, head_extra=f'<script type="application/ld+json">{json.dumps(ORG_LD)}</script>\n<script src="/static/hero.js?v={HERO_V}" defer></script>')


def page_services():
    rows = "".join(f"""
    <article class="svc-row" id="{sv['id']}">
      <div class="main">
        <div class="icon-tile">{icon(sv['icon'])}</div>
        <h2>{e(sv['title'])}</h2>
        <p>{e(sv['summary'])}</p>
        <ul class="checks">{''.join(f'<li>{icon("check")}{e(p)}</li>' for p in sv['points'])}</ul>
      </div>
      <div class="side">
        <div><h4>Ideal for</h4><p>{e(sv['ideal'])}</p></div>
        <div><h4>Typical deliverables</h4><ul class="deliv">{''.join(f'<li>{e(d)}</li>' for d in sv['deliverables'])}</ul></div>
        <div class="stores"><a class="btn btn-ink btn-sm" href="/services/{sv['slug']}">Learn more{ARROW}</a>{contact_btn("Discuss this service", "services_row", TOPICS[0], cls="btn btn-ghost btn-sm")}</div>
      </div>
    </article>""" for sv in SERVICES)
    proofs = "".join(f"""
      <div class="proof-card">
        <div class="icon-tile">{icon(ic)}</div>
        <h3>{e(t)}</h3>
        <p>{e(d)}</p>
        <a class="where" href="/apps/{s}"><img src="/static/apps/{s}.png" alt="{e(BY_SLUG[s]['name'])} app icon" width="28" height="28" loading="lazy">{e(BY_SLUG[s]['name'])} <em>on iOS &amp; Android</em></a>
      </div>""" for ic, t, s, d in PROOFS)
    steps = [
        ("Discovery", "A short call to understand your product, users, and goals."),
        ("Scope & proposal", "A clear plan with milestones, deliverables, timeline, and cost."),
        ("Build & iterate", "Regular demos and shared progress, so you always see where things stand."),
        ("Launch & handoff", "Store submission, launch support, and documentation your team can own."),
    ]
    timeline = "".join(f'<li><span class="dot">{i + 1:02d}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i, (t, d) in enumerate(steps))
    ld = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "DNNR Tech", "url": f"{SITE}/services",
          "areaServed": "Worldwide", "address": ORG_LD["address"],
          "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Consulting services",
                              "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": sv["title"], "description": sv["summary"]}} for sv in SERVICES]}}
    body = f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow"><span class="dot"></span>Consulting · {CITY}</span>
      <h1 class="display" style="font-size:clamp(40px,5.6vw,68px)">Build your AI product with a team that ships.</h1>
      <p class="lead">We design, build, and operate AI-powered apps of our own. We bring that experience to founders, from the first prototype to the App Store.</p>
      <div class="actions">
        {contact_btn("Start a project", "services_hero", TOPICS[0], with_arrow=True)}
        <a class="btn btn-ghost" href="#process">How it works</a>
      </div>
    </div>
    {ART_ROADMAP}
  </div>
</section>

<section style="padding-top:40px">
  <div class="container">
    {section_head("Services", "What we can do for you.")}
    <div class="svc-rows">{rows}</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container editorial">
    <div class="intro">
      <span class="kicker">Why DNNR Tech</span>
      <h2 class="h2" style="margin-top:14px">We build what<br>we recommend.</h2>
      <p>Our advice comes from products we run ourselves, not from slide decks.</p>
    </div>
    <ol class="plist">
      <li><span class="n">01</span><div><h3>We ship our own products</h3><p>Our AI-powered apps are live on the App Store and Google Play. We know what it takes to get from prototype to approved, updated, and used.</p></div></li>
      <li><span class="n">02</span><div><h3>Production AI experience</h3><p>Multimodal and generative AI, semantic search, AI trust &amp; safety, AI data pipelines, and on-device ML, all running in production apps.</p></div></li>
      <li><span class="n">03</span><div><h3>Based in Silicon Valley</h3><p>Headquartered in San Jose, California, and working remotely with teams anywhere.</p></div></li>
    </ol>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("In production", "AI we've shipped.", "Each capability below runs in one of our own apps today.")}
    <div class="proof-grid">{proofs}</div>
  </div>
</section>

<section id="process" style="padding-top:0">
  <div class="container">
    {section_head("Process", "How an engagement works.")}
    <ol class="timeline">{timeline}</ol>
  </div>
</section>

<section id="contact" style="padding-top:0">
  <div class="container contact-layout">
    <div class="info">
      <span class="kicker">Contact</span>
      <h2 class="h2" style="margin:14px 0 16px">Tell us what<br>you're building.</h2>
      <p>Share a few details and we'll reply with next steps.</p>
      <ul>
        <li><div class="icon-tile">{icon("message")}</div><div><b>What to include</b><span>Your idea or product, current stage, timeline, and anything you've already built.</span></div></li>
        <li><div class="icon-tile">{icon("clock")}</div><div><b>When we reply</b><span>Usually within a few business days.</span></div></li>
        <li><div class="icon-tile">{icon("pin")}</div><div><b>Where we are</b><span>{CITY}. Working remotely with teams anywhere.</span></div></li>
      </ul>
    </div>
    <div class="form-card">{contact_form("services_form", idp="svc")}</div>
  </div>
</section>"""
    return layout(path="/services", title="Startup Product & AI Consulting", current="services",
                  description="AI product and MVP development, native iOS and Android app development with backend, and AI integration advisory for startups, from a San Jose team that ships its own AI products.",
                  body=body, head_extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>')


def page_apps():
    used = [c for c in REG["categories"] if any(a["category"] == c["id"] for a in APPS)]
    some_ai = 0 < sum(1 for a in APPS if a.get("ai")) < len(APPS)  # an AI filter only helps if not every app has AI
    chips = ('<button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>'
             + (f'<button class="chip" type="button" data-filter="ai" aria-pressed="false">{icon("sparkle")}AI-powered</button>' if some_ai else "")
             + "".join(f'<button class="chip" type="button" data-filter="{c["id"]}" aria-pressed="false">{e(c["label"])}</button>' for c in used))
    cards = "".join(f"""
      <article class="app-card" id="{a['slug']}" data-cat="{a['category']}" data-ai="{'1' if a.get('ai') else '0'}">
        <div class="body">
          <div class="head"><img class="icon" src="/static/apps/{a['slug']}.png" alt="{e(a['name'])} app icon" width="64" height="64" loading="lazy">{ai_badge(a)}</div>
          <div><h3><a class="stretch" href="/apps/{a['slug']}">{e(a['name'])}</a></h3><div class="cat">{e(CATS[a['category']])}</div></div>
          <p>{e(a['tagline'])}</p>
        </div>
        <div class="links">
          <a href="{ios_url(a)}" rel="noopener" aria-label="{e(a['name'])} on the App Store">{APPLE}App Store</a>
          <a href="{play_url(a)}" rel="noopener" aria-label="{e(a['name'])} on Google Play">{PLAY}Google Play</a>
        </div>
      </article>""" for a in APPS)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1,
         "item": {"@type": "MobileApplication", "name": a["name"], "description": a["tagline"], "operatingSystem": "iOS, Android",
                  "applicationCategory": CATS[a["category"]], "url": f"{SITE}/apps/{a['slug']}", "image": f"{SITE}/static/apps/{a['slug']}.png",
                  "sameAs": [ios_url(a), play_url(a)], "author": {"@type": "Organization", "name": "DNNR Tech"}}}
        for i, a in enumerate(APPS)]}
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>Portfolio</span>
    <h1>Our apps</h1>
    <p class="lead">AI-powered products we design, build, and operate ourselves, from multimodal and generative AI to privacy-first on-device intelligence. Available on the App Store and Google Play.</p>
    <div class="stores" style="margin-top:24px">
      <a class="btn btn-ghost btn-sm" href="/ios">{APPLE}App Store</a>
      <a class="btn btn-ghost btn-sm" href="/android">{PLAY}Google Play</a>
    </div>
  </div>
  <div class="chips" role="group" aria-label="Filter apps">{chips}</div>
  <div class="app-grid" style="margin-bottom:56px">{cards}</div>
</div>
{cta("Want to build an app like these?", "We help startups design, build, and launch AI-powered apps.", "apps_cta", "Start a project")}"""
    return layout(path="/apps", title="Apps", current="apps",
                  description="AI-powered iPhone and Android apps built and operated by DNNR Tech: What to Eat, TJ Near & Hot, AutoMiles, Golf Passport, StampRescue, Targeted Resume AI, and more.",
                  body=body, head_extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>')



def breadcrumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def crumbs(items):
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span>/</span> '.join(
        f'<a href="{u}">{e(n)}</a>' if i < len(items) - 1 else f'<span aria-current="page">{e(n)}</span>' for i, (n, u) in enumerate(items)) + '</nav>'


def page_service_detail(sv):
    path = f"/services/{sv['slug']}"
    related = "".join(f"""
      <a class="work-card" href="/apps/{a['slug']}">
        <div class="top"><img class="icon" src="/static/apps/{a['slug']}.png" alt="{e(a['name'])} app icon" width="56" height="56" loading="lazy">{ai_badge(a)}</div>
        <h3>{e(a['name'])}</h3>
        <p>{e(a.get('ai_story') or a['description'])}</p>
      </a>""" for a in (BY_SLUG[x] for x in sv["related"]))
    faq = "".join(f'<details class="faq-item"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in sv["faq"])
    others = "".join(f'<a class="service" href="/services/{o["slug"]}"><div class="icon-tile">{icon(o["icon"])}</div><h3>{e(o["title"])}</h3><p>{e(o["summary"])}</p><span class="more">Learn more {ARROW}</span></a>'
                     for o in SERVICES if o is not sv)
    steps = [("Discovery", "A short call to understand your product, users, and goals."),
             ("Scope & proposal", "A clear plan with milestones, deliverables, timeline, and cost."),
             ("Build & iterate", "Regular demos and shared progress, so you always see where things stand."),
             ("Launch & handoff", "Launch support and documentation your team can own.")]
    timeline = "".join(f'<li><span class="dot">{i + 1:02d}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i, (t, d) in enumerate(steps))
    trail = [("Home", "/"), ("Services", "/services"), (sv["title"], path)]
    ld = [
        {"@context": "https://schema.org", "@type": "Service", "name": sv["title"], "description": sv["summary"], "url": SITE + path,
         "serviceType": sv["title"], "areaServed": "Worldwide",
         "provider": {"@type": "Organization", "name": "DNNR Tech", "url": SITE, "address": ORG_LD["address"]}},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in sv["faq"]]},
        breadcrumbs_ld(trail),
    ]
    body = f"""
<div class="container">
  <div class="doc-hero detail-hero">
    {crumbs(trail)}
    <div class="icon-tile" style="margin-top:22px">{icon(sv['icon'])}</div>
    <h1>{e(sv['title'])}</h1>
    <p class="lead">{e(sv['summary'])} {e(sv['ideal'])}</p>
    <div class="actions" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:28px">
      {contact_btn("Start a project", "service_" + sv['id'], TOPICS[0], with_arrow=True)}
      <a class="btn btn-ghost" href="/services">All services</a>
    </div>
  </div>
</div>

<section style="padding-top:24px">
  <div class="container">
    <article class="svc-row" style="scroll-margin-top:0">
      <div class="main">
        <span class="kicker">What's included</span>
        <ul class="checks">{''.join(f'<li>{icon("check")}{e(p)}</li>' for p in sv['points'])}</ul>
      </div>
      <div class="side">
        <div><h4>Ideal for</h4><p>{e(sv['ideal'])}</p></div>
        <div><h4>Typical deliverables</h4><ul class="deliv">{''.join(f'<li>{e(d)}</li>' for d in sv['deliverables'])}</ul></div>
      </div>
    </article>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("Proof", "Built and run by us.", "Apps of our own that use the same skills.")}
    <div class="work">{related}</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("Process", "How an engagement works.")}
    <ol class="timeline">{timeline}</ol>
  </div>
</section>

<section style="padding-top:0">
  <div class="container editorial">
    <div class="intro"><span class="kicker">FAQ</span><h2 class="h2" style="margin-top:14px">Common questions</h2></div>
    <div class="faq">{faq}</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("More services", "Other ways we can help.")}
    <div class="services" style="grid-template-columns:repeat(2,1fr)">{others}</div>
  </div>
</section>
{cta("Ready to talk about your project?", "Tell us what you're building. We'll reply by email with next steps.", "service_" + sv['id'], "Start a conversation")}"""
    return layout(path=path, title=sv["title"], current="services",
                  description=f"{sv['summary']} {sv['ideal']} From DNNR Tech, a San Jose AI technology company.",
                  body=body, head_extra="\n".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld))


def page_app_detail(a):
    path = f"/apps/{a['slug']}"
    shots = "".join(f'<img src="/static/apps/shots/{a["slug"]}-{i}.jpg" alt="{e(a["name"])} screenshot {i}" width="360" height="780" loading="lazy">'
                    for i in (1, 2, 3) if (ROOT / "static" / "apps" / "shots" / f"{a['slug']}-{i}.jpg").exists())
    more = [x for x in APPS if x["slug"] != a["slug"] and x["category"] == a["category"]][:3]
    if len(more) < 3:
        more += [x for x in APPS if x["slug"] != a["slug"] and x not in more][: 3 - len(more)]
    more_html = "".join(f"""
      <a class="work-card" href="/apps/{x['slug']}">
        <div class="top"><img class="icon" src="/static/apps/{x['slug']}.png" alt="{e(x['name'])} app icon" width="56" height="56" loading="lazy">{ai_badge(x)}</div>
        <h3>{e(x['name'])}</h3><p>{e(x['tagline'])}</p>
      </a>""" for x in more)
    ai_block = f"""
    <div class="callout ai-callout"><span class="ai-badge">{icon("sparkle")}{e(a['ai'])}</span><p>{e(a['ai_story'])}</p></div>""" if a.get("ai") else ""
    trail = [("Home", "/"), ("Apps", "/apps"), (a["name"], path)]
    ld = [
        {"@context": "https://schema.org", "@type": "MobileApplication", "name": a["name"], "description": a["description"],
         "url": SITE + path, "image": f"{SITE}/static/apps/{a['slug']}.png", "operatingSystem": "iOS, Android",
         "applicationCategory": CATS[a["category"]], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "installUrl": [ios_url(a), play_url(a)], "sameAs": [ios_url(a), play_url(a)],
         "author": {"@type": "Organization", "name": "DNNR Tech", "url": SITE}},
        breadcrumbs_ld(trail),
    ]
    extra = '<p><a href="/academic_cv_support">Academic CV AI support and AI content reports</a></p>' if a["slug"] == "academic-cv-ai" else ""
    body = f"""
<div class="container">
  <div class="doc-hero detail-hero">
    {crumbs(trail)}
    <div class="app-hero">
      <img class="app-hero-icon" src="/static/apps/{a['slug']}.png" alt="{e(a['name'])} app icon" width="112" height="112">
      <div>
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap"><span class="kicker">{e(CATS[a['category']])}</span>{ai_badge(a)}</div>
        <h1>{e(a['name'])}</h1>
        <p class="lead">{e(a['tagline'])}</p>
        <div class="stores" style="margin-top:22px">
          <a class="btn btn-ink" href="{ios_url(a)}" rel="noopener">{APPLE}App Store</a>
          <a class="btn btn-ghost" href="{play_url(a)}" rel="noopener">{PLAY}Google Play</a>
        </div>
      </div>
    </div>
  </div>
</div>

<section style="padding-top:16px">
  <div class="container app-detail">
    <div class="prose">
      <p>{e(a['description'])}</p>
      {ai_block}
      <h2>Highlights</h2>
      <ul class="checks" style="grid-template-columns:1fr">{''.join(f'<li>{icon("check")}{e(h)}</li>' for h in a['highlights'])}</ul>
      <p class="muted-links">Free on the App Store and Google Play. <a href="/support">Support</a> · <a href="/privacy-policy">Privacy Policy</a> · <a href="/delete-account">Data deletion</a></p>
      {extra}
    </div>
    <div class="shots" aria-label="Screenshots">{shots}</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    {section_head("More from DNNR Tech", "You might also like.", "", '<a class="btn btn-ghost" href="/apps">All apps</a>')}
    <div class="work">{more_html}</div>
  </div>
</section>"""
    return layout(path=path, title=a.get("seo_title") or f"{a['name']} — {a['tagline'].rstrip('.')}", current="apps",
                  description=f"{a['description']} Free on iPhone and Android.",
                  body=body, head_extra="\n".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld))


def llms_txt(full=False):
    L = ["# DNNR Tech", "",
         "> DNNR Tech is a technology company based in San Jose, California (Silicon Valley). It builds AI-powered consumer apps "
         "for iOS and Android and provides startup consulting: AI product and MVP development, mobile app development, and AI "
         "integration advisory. Motto: \"Daily Needs, Naturally Refined.\"", "",
         "Contact: use the form at https://dnnr.us/contact (we reply by email). All apps are free on the App Store and Google Play.", ""]
    L += ["## Company", "",
          f"- [Home]({SITE}/): What DNNR Tech does — AI products and startup consulting.",
          f"- [Services]({SITE}/services): Consulting services, process, and AI we've shipped.",
          f"- [Apps]({SITE}/apps): All DNNR Tech apps for iPhone and Android.",
          f"- [Contact]({SITE}/contact): Contact form for projects, partnerships, and app support.", ""]
    L += ["## Consulting services", ""]
    for sv in SERVICES:
        L.append(f"- [{sv['title']}]({SITE}/services/{sv['slug']}): {sv['summary']} Ideal for: {sv['ideal']}")
        if full:
            L += [f"  - Includes: {'; '.join(sv['points'])}.", f"  - Typical deliverables: {'; '.join(sv['deliverables'])}."]
            L += [f"  - Q: {q} A: {a}" for q, a in sv["faq"]]
    L += ["", "## Apps (free on iOS and Android)", ""]
    for a in APPS:
        ai = f" AI: {a['ai_story']}" if a.get("ai_story") else ""
        L.append(f"- [{a['name']}]({SITE}/apps/{a['slug']}): {a['tagline']}{ai}")
        if full:
            L += [f"  - {a['description']}", f"  - Highlights: {'; '.join(a['highlights'])}.",
                  f"  - App Store: {ios_url(a)}", f"  - Google Play: {play_url(a)}"]
    L += ["", "## Policies", "",
          f"- [Privacy Policy]({SITE}/privacy-policy): How DNNR Tech apps and dnnr.us handle personal information.",
          f"- [Support]({SITE}/support): Help with any DNNR Tech app.",
          f"- [Data & account deletion]({SITE}/delete-account): How to delete your data.", ""]
    if not full:
        L += ["## Optional", "", f"- [Full details]({SITE}/llms-full.txt): Services and apps with full descriptions and FAQs.", ""]
    return "\n".join(L)


def page_contact():
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>Contact</span>
    <h1>Let's talk.</h1>
    <p class="lead">Questions about a project, a partnership, or one of our apps? Send us a message.</p>
  </div>
  <div class="contact-layout" style="padding-bottom:104px">
    <div class="info">
      <ul style="margin-top:0">
        <li><div class="icon-tile">{icon("rocket")}</div><div><b>Consulting &amp; projects</b><span>AI products, MVPs, mobile apps, and AI integration.</span></div></li>
        <li><div class="icon-tile">{icon("users")}</div><div><b>Partnerships</b><span>Distribution, co-marketing, and collaboration.</span></div></li>
        <li><div class="icon-tile">{icon("message")}</div><div><b>App support</b><span>Help with any of our apps. See also <a href="/support">Support</a>.</span></div></li>
        <li><div class="icon-tile">{icon("clock")}</div><div><b>Response time</b><span>Usually within a few business days.</span></div></li>
      </ul>
    </div>
    <div class="form-card">{contact_form("contact_page", idp="cp")}</div>
  </div>
</div>"""
    return layout(path="/contact", title="Contact", description="Contact DNNR Tech about consulting, partnerships, or app support.", body=body, dialog=False)


def page_privacy():
    en, ko = content("privacy_en.html"), content("privacy_ko.html")

    def expand(text):
        return re.sub(r"\{\{app:([a-z0-9-]+)\}\}",
                      lambda m: f'<img src="/static/apps/{m.group(1)}.png" alt="{e(BY_SLUG[m.group(1)]["name"])} app icon" width="32" height="32">{e(BY_SLUG[m.group(1)]["name"])}', text)

    eff = content("privacy_date.txt").strip()
    d = date.fromisoformat(eff)
    en = expand(en).replace("{{effective}}", f"{d:%B} {d.day}, {d.year}")
    ko = expand(ko).replace("{{effective}}", f"{d.year}년 {d.month}월 {d.day}일")
    en_page = doc_page(path="/privacy-policy", title="Privacy Policy", eyebrow="Legal", heading="Privacy Policy",
                       description="How DNNR Tech apps and this website collect, use, and protect your information.",
                       meta=f"Effective {eff} · Applies to all DNNR Tech apps and dnnr.us", body_html=en, toc=toc_from(en))
    ko_page = doc_page(path="/ko/privacy-policy", title="개인정보처리방침", lang="ko", eyebrow="Legal", heading="개인정보처리방침",
                       description="DNNR Tech 앱과 웹사이트의 개인정보 수집·이용·보호 방식.",
                       meta=f'시행일 {eff} · DNNR Tech의 모든 앱과 dnnr.us에 적용 · <a href="/privacy-policy">English</a>', body_html=ko, toc=toc_from(ko))
    return en_page, ko_page


def page_support():
    en_page = doc_page(path="/support", title="Support", current="support", eyebrow="Help center", heading="How can we help?",
                       description="Get help with DNNR Tech apps and request deletion of your data.",
                       meta="Support for every app published by DNNR Tech.", body_html=content("support_en.html"))
    ko_page = doc_page(path="/ko/support", title="고객 지원", lang="ko", eyebrow="Help center", heading="무엇을 도와드릴까요?",
                       description="DNNR Tech 앱 고객 지원 및 데이터 삭제 요청 안내.",
                       meta='DNNR Tech의 모든 앱에 대한 지원 페이지입니다. · <a href="/support">English</a>', body_html=content("support_ko.html"))
    return en_page, ko_page


def page_delete():
    en_page = doc_page(path="/delete-account", title="Data & Account Deletion", eyebrow="Your data", heading="Data &amp; account deletion",
                       description="How to delete your account and data in DNNR Tech apps.",
                       meta="Applies to all apps published by DNNR Tech.", body_html=content("delete_en.html"))
    ko_page = doc_page(path="/ko/delete-account", title="데이터 및 계정 삭제", lang="ko", eyebrow="Your data", heading="데이터 및 계정 삭제",
                       description="DNNR Tech 앱의 계정 및 데이터 삭제 방법.",
                       meta='DNNR Tech가 출시한 모든 앱에 적용됩니다. · <a href="/delete-account">English</a>', body_html=content("delete_ko.html"))
    return en_page, ko_page


def page_academic_cv():
    a = BY_SLUG["academic-cv-ai"]
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>App support</span>
    <div class="app-head" style="margin-top:20px"><img class="app-icon" src="/static/apps/{a['slug']}.png" alt="{e(a['name'])} app icon" width="60" height="60"><h1 style="margin:0">Academic CV AI Support</h1></div>
  </div>
  <div class="doc-layout single">
    <article class="prose">
      <p>We're here to help with questions, feedback, or problems with Academic CV AI.</p>
      <div class="callout">
        <p><strong>Report AI-generated content</strong><br>If the app produced inaccurate, offensive, or otherwise inappropriate content, please report it using the form below. Include what you asked for and what the app generated.</p>
        <p><a class="btn btn-ink" href="https://docs.google.com/forms/d/e/1FAIpQLSd93aXKlpX-oVZQFGrBTV-Up8HwOm6N-n3ETrGO8LjfgyNn2w/viewform?usp=dialog" rel="noopener">Submit a report</a></p>
      </div>
      <p>For anything else, {contact_btn("send us a message", "support_contact", "App support", cls="")}.</p>
      <p>See also: <a href="/support">Support</a> · <a href="/privacy-policy#ai">Privacy Policy (AI features)</a> · <a href="/delete-account">Data deletion</a></p>
      <div class="stores"><a class="btn btn-ghost btn-sm" href="{ios_url(a)}" rel="noopener">{APPLE}App Store</a><a class="btn btn-ghost btn-sm" href="{play_url(a)}" rel="noopener">{PLAY}Google Play</a></div>
    </article>
  </div>
</div>"""
    return layout(path="/academic_cv_support", title="Academic CV AI Support", description="Support and AI content reporting for Academic CV AI.", body=body)


def page_404():
    body = """
<div class="container notfound">
  <div>
    <div class="code grad">404</div>
    <h1 class="h2" style="margin-top:12px">This page doesn't exist.</h1>
    <p class="lead" style="margin:14px auto 28px">The link may be old or mistyped. Try one of these instead.</p>
    <div class="stores" style="justify-content:center">
      <a class="btn btn-ink" href="/">Home</a><a class="btn btn-ghost" href="/services">Services</a><a class="btn btn-ghost" href="/apps">Apps</a>
    </div>
  </div>
</div>"""
    return layout(path="/404", title="Page not found", description="Page not found.", body=body, head_extra='<meta name="robots" content="noindex">')


def sitemap():
    paths = (["/", "/services"] + [f"/services/{sv['slug']}" for sv in SERVICES] + ["/apps"] + [f"/apps/{a['slug']}" for a in APPS]
             + ["/contact", "/support", "/delete-account", "/privacy-policy", "/academic_cv_support"])
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def main():
    privacy_en, privacy_ko = page_privacy()
    support_en, support_ko = page_support()
    delete_en, delete_ko = page_delete()
    pages = {
        "index.html": page_home(),
        "services.html": page_services(),
        "apps.html": page_apps(),
        "contact.html": page_contact(),
        "privacy-policy.html": privacy_en,
        "support.html": support_en,
        "delete-account.html": delete_en,
        "ko/privacy-policy.html": privacy_ko,
        "ko/support.html": support_ko,
        "ko/delete-account.html": delete_ko,
        "academic_cv_support.html": page_academic_cv(),
        "404.html": page_404(),
        **{f"services/{sv['slug']}.html": page_service_detail(sv) for sv in SERVICES},
        **{f"apps/{a['slug']}.html": page_app_detail(a) for a in APPS},
        "llms.txt": llms_txt(),
        "llms-full.txt": llms_txt(full=True),
        "sitemap.xml": sitemap(),
        "robots.txt": f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
    }
    for name, text in pages.items():
        (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / name).write_text(text)
    missing = [a["slug"] for a in APPS if not (ROOT / "static" / "apps" / f"{a['slug']}.png").exists()]
    if missing:
        raise SystemExit(f"Missing icons in static/apps/: {missing}")
    print(f"Built {len(pages)} files for {len(APPS)} apps.")


if __name__ == "__main__":
    main()
