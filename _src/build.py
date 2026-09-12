#!/usr/bin/env python3
"""Build dnnr.us static pages from _src/ into the repo root.

    python3 _src/build.py

Inputs:  _src/apps.json (app registry), _src/content/*.html (long-form copy)
Outputs: index.html, apps.html, privacy-policy.html, support.html,
         delete-account.html, ko/{privacy-policy,support,delete-account}.html
         (Korean, reachable only by URL), academic_cv_support.html, 404.html,
         sitemap.xml, robots.txt

The repo root is served as-is by Cloudflare Pages (dnnr.us) and GitHub Pages
(dnnr.mrsap.com), so generated files are committed. Do not hand-edit them.
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
CATS = {c["id"]: c["label"] for c in REG["categories"]}

APPLE_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.37 12.64c-.02-2.24 1.83-3.32 1.91-3.37-1.04-1.52-2.66-1.73-3.24-1.75-1.38-.14-2.69.81-3.39.81-.7 0-1.78-.79-2.92-.77-1.5.02-2.89.87-3.66 2.22-1.56 2.71-.4 6.72 1.12 8.91.74 1.07 1.63 2.28 2.8 2.23 1.12-.04 1.55-.73 2.9-.73 1.36 0 1.74.73 2.93.71 1.21-.02 1.98-1.09 2.72-2.17.86-1.25 1.21-2.46 1.23-2.52-.03-.01-2.36-.9-2.4-3.57zM14.14 6.07c.62-.75 1.04-1.8.92-2.84-.89.04-1.97.59-2.61 1.34-.57.66-1.07 1.73-.94 2.75.99.08 2.01-.5 2.63-1.25z"/></svg>'
PLAY_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.6 2.3c-.3.3-.4.7-.4 1.2v17c0 .5.1.9.4 1.2l9.4-9.7L4.6 2.3zm10.8 11.1 2.8 2.9-11.6 6.6c-.4.2-.8.3-1.1.2l9.9-9.7zm4.4-3.6c.7.4 1 .9 1 1.4s-.3 1.1-1 1.4l-2.5 1.4-3-3.1 3-3.1 2.5 2zM6.6 1.1l11.6 6.6-2.8 2.9-9.9-9.7c.3-.1.7 0 1.1.2z"/></svg>'
WEB_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>'
MAIL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'

e = html.escape


def ios_url(a):
    return f"https://apps.apple.com/app/id{a['ios_id']}"


def play_url(a):
    return f"https://play.google.com/store/apps/details?id={a['android_id']}"


def store_buttons(a, size="btn-sm"):
    out = []
    if a.get("ios_id"):
        out.append(f'<a class="btn btn-ghost {size}" href="{ios_url(a)}" rel="noopener">{APPLE_SVG}App Store</a>')
    if a.get("android_id"):
        out.append(f'<a class="btn btn-ghost {size}" href="{play_url(a)}" rel="noopener">{PLAY_SVG}Google Play</a>')
    if a.get("web"):
        out.append(f'<a class="btn btn-ghost {size}" href="{a["web"]}" rel="noopener">{WEB_SVG}Web</a>')
    return '<div class="stores">' + "".join(out) + "</div>"


def app_card(a):
    return f"""
      <article class="card" id="{a['slug']}" data-cat="{a['category']}" data-ai="{'1' if a.get('ai') else '0'}">
        <div class="app-head">
          <img class="app-icon" src="/static/apps/{a['slug']}.png" alt="" width="60" height="60" loading="lazy">
          <div><h3>{e(a['name'])}</h3><div class="cat">{e(CATS[a['category']])}</div></div>
          {f'<span class="badge-ai" title="AI feature">{e(a["ai"])}</span>' if a.get("ai") else ""}
        </div>
        <p>{e(a['tagline'])}</p>
        {store_buttons(a)}
      </article>"""


def layout(*, path, title, description, body, current="", head_extra="", scripts="", lang="en"):
    canonical = SITE + (path if path != "/index" else "/")
    full_title = title if title.startswith("DNNR Tech") else f"{title} — DNNR Tech"
    nav = [("/services", "Services", "services", ""), ("/apps", "Apps", "apps", ""), ("/support", "Support", "support", "hide-sm")]
    cur = ' aria-current="page"'
    nav_html = "".join(
        f'<a class="{cls}" href="{href}"{cur if key == current else ""}>{label}</a>'
        for href, label, key, cls in nav
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#FAFAFB" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0B0B10" media="(prefers-color-scheme: dark)">
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
<link rel="stylesheet" href="/static/site.css">
{head_extra}
</head>
<body>
<header class="site-header">
  <div class="container bar">
    <a class="brand" href="/" aria-label="DNNR Tech home"><img src="/static/dnnr-mark.png" alt="" width="34" height="19">DNNR Tech</a>
    <nav class="nav" aria-label="Primary">{nav_html}<a class="btn btn-ink btn-sm" href="mailto:{EMAIL}">Contact</a></nav>
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
        <p>AI products and startup consulting from {CITY}.</p>
      </div>
      <div><b>Company</b><a href="/services">Services</a><a href="/apps">Apps</a><a href="/ios">iOS apps</a><a href="/android">Android apps</a></div>
      <div><b>Help</b><a href="/support">Support</a><a href="/delete-account">Data deletion</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
      <div><b>Legal</b><a href="/privacy-policy">Privacy Policy</a><a href="/app-ads.txt">app-ads.txt</a></div>
    </div>
    <div class="copyright"><span>© {YEAR} DNNR Tech. All rights reserved.</span><span>Apps are independent and not affiliated with the brands they reference.</span></div>
  </div>
</footer>
<script>
  (function () {{
    var h = document.querySelector('.site-header');
    var on = function () {{ h.classList.toggle('scrolled', window.scrollY > 4); }};
    on(); window.addEventListener('scroll', on, {{ passive: true }});
  }})();
</script>
{scripts}
</body>
</html>
"""


OPEN_DETAILS_SCRIPT = """<script>
  (function () {
    function open() {
      var el = location.hash && document.getElementById(location.hash.slice(1));
      if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
    }
    open(); window.addEventListener('hashchange', open);
  })();
</script>"""


def doc_page(*, path, title, description, eyebrow, heading, meta="", body_html, toc=None, current="", extra_scripts="", lang="en", alt_link=""):
    """One single-language document page. English lives at /<page>; Korean at /ko/<page> (not linked from English pages)."""
    toc_html = ""
    if toc:
        label = "목차" if lang == "ko" else "On this page"
        toc_html = f'<nav class="toc" aria-label="{label}"><b>{label}</b>' + "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in toc) + "</nav>"
    layout_cls = "doc-layout" if toc else "doc-layout single"
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>{e(eyebrow)}</span>
    <h1>{heading}</h1>
    <p class="meta">{meta}{alt_link}</p>
  </div>
  <div class="{layout_cls}">
    {toc_html}
    <article class="prose" lang="{lang}">{body_html}</article>
  </div>
</div>"""
    return layout(path=path, title=title, description=description, body=body, current=current, scripts=extra_scripts, lang=lang)


def content(name):
    return (SRC / "content" / name).read_text()


def toc_from(html_text):
    return re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', html_text)


# ---------------- pages ----------------

ORG_LD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "DNNR Tech",
    "url": SITE,
    "logo": f"{SITE}/static/icon-512.png",
    "email": EMAIL,
    "description": "San Jose-based technology company building AI-powered mobile apps and providing startup product, mobile, and AI consulting.",
    "address": {"@type": "PostalAddress", "addressLocality": "San Jose", "addressRegion": "CA", "addressCountry": "US"},
    "knowsAbout": ["Artificial intelligence", "Large language models", "Mobile app development", "Flutter", "MVP development"],
    "sameAs": ["https://www.linkedin.com/company/dnnr-us/", "https://apps.apple.com/developer/id1668952055",
               "https://play.google.com/store/apps/dev?id=6001862912587595419"],
}

SERVICES = [
    {
        "id": "mvp",
        "title": "AI product & MVP development",
        "summary": "Turn an idea into a launch-ready product with AI at its core.",
        "points": ["Product scoping and a lean feature plan", "Clickable prototype to validate early",
                   "AI feature design: vision, text, search, moderation", "MVP build, testing, and launch"],
    },
    {
        "id": "mobile",
        "title": "Mobile app development",
        "summary": "Native-quality iOS and Android apps from one Flutter codebase.",
        "points": ["Flutter apps for iPhone, iPad, and Android", "Firebase and Google Cloud backends",
                   "Analytics, in-app purchases, and ads", "App Store and Google Play submission"],
    },
    {
        "id": "ai",
        "title": "AI integration advisory",
        "summary": "Add practical LLM features to your product, with costs under control.",
        "points": ["Where AI helps users, and where it doesn't", "Model selection: Gemini, Claude, OpenAI",
                   "Prompt design, evaluation, and guardrails", "Cost, latency, and privacy architecture"],
    },
]

CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>'
ARROW = '<span aria-hidden="true">→</span>'


def service_card(sv, full=False):
    pts = "".join(f"<li>{CHECK_SVG}{e(p)}</li>" for p in sv["points"]) if full else ""
    return f"""
      <article class="service" id="{sv['id']}">
        <h3>{e(sv['title'])}</h3>
        <p>{e(sv['summary'])}</p>
        {f'<ul class="checks">{pts}</ul>' if full else ''}
      </article>"""


def page_home():
    featured = [a for a in APPS if a.get("featured")]
    ai_count = sum(1 for a in APPS if a.get("ai"))
    mosaic = "".join(
        f'<a href="/apps#{a["slug"]}" title="{e(a["name"])}"><img src="/static/apps/{a["slug"]}.png" alt="{e(a["name"])}" width="128" height="128"></a>'
        for a in APPS[:12]
    )
    body = f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow"><span class="dot"></span>{CITY} · Silicon Valley</span>
      <h1 class="display">We build AI products<span class="grad"> and help startups ship theirs.</span></h1>
      <p class="lead">DNNR Tech is a San Jose–based technology company. We design, build, and run our own AI-powered mobile apps, and we bring that hands-on experience to founders as a product, mobile, and AI engineering partner.</p>
      <div class="actions">
        <a class="btn btn-ink" href="/services">Work with us</a>
        <a class="btn btn-ghost" href="/apps">See our apps</a>
      </div>
      <div class="stats">
        <div><b>{len(APPS)}</b><span>apps shipped</span></div>
        <div><b>{ai_count}</b><span>with AI features</span></div>
        <div><b>iOS &amp; Android</b><span>every app, both stores</span></div>
      </div>
    </div>
    <div class="mosaic" aria-hidden="true">{mosaic}</div>
  </div>
</section>

<section style="padding-top:24px">
  <div class="container">
    <div class="section-head"><div><div class="rule"></div><h2 class="h2">What we do</h2><p>Two sides of one company: we make products, and we help others make theirs.</p></div></div>
    <div class="pillars">
      <a class="pillar" href="/apps">
        <span class="kicker">Products</span>
        <h3>AI-powered apps</h3>
        <p>We build and operate a portfolio of consumer apps on the App Store and Google Play, from reading foreign menus with vision AI to tailoring resumes with large language models.</p>
        <span class="more">Explore our apps {ARROW}</span>
      </a>
      <a class="pillar pillar-ink" href="/services">
        <span class="kicker">Consulting</span>
        <h3>Startup product &amp; AI consulting</h3>
        <p>We help founders go from idea to launched product: scoping an MVP, building iOS and Android apps, and adding AI features that are useful, reliable, and affordable to run.</p>
        <span class="more">Our services {ARROW}</span>
      </a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <div><div class="rule"></div><h2 class="h2">Consulting services</h2><p>Hands-on help from a team that ships its own products.</p></div>
      <a class="btn btn-ghost" href="/services">How we work</a>
    </div>
    <div class="services">{"".join(service_card(sv) for sv in SERVICES)}</div>
  </div>
</section>

<section style="padding-top:24px">
  <div class="container">
    <div class="section-head">
      <div><div class="rule"></div><h2 class="h2">Built and run by us</h2><p>Selected apps from our portfolio. Every one is live on both stores.</p></div>
      <a class="btn btn-ghost" href="/apps">View all {len(APPS)} apps</a>
    </div>
    <div class="grid">{"".join(app_card(a) for a in featured)}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><div><div class="rule"></div><h2 class="h2">How we build</h2></div></div>
    <div class="principles">
      <div class="principle"><div class="num">01</div><h3>Ship early, learn fast</h3><p>Small scope, real users, quick iterations. We launch, measure, and improve instead of polishing in private.</p></div>
      <div class="principle"><div class="num">02</div><h3>Practical AI</h3><p>We use AI where it saves people time, and we design for cost, speed, and failure cases from day one.</p></div>
      <div class="principle"><div class="num">03</div><h3>Built to operate</h3><p>Analytics, store compliance, and privacy are part of the product, not an afterthought. <a href="/privacy-policy">Our privacy policy</a></p></div>
    </div>
  </div>
</section>

<section style="padding-top:16px">
  <div class="container">
    <div class="band">
      <div><h2>Building something with AI?</h2><p>Tell us about your product and timeline. We usually reply within a few business days.</p></div>
      <a class="btn" href="mailto:{EMAIL}?subject=Consulting%20inquiry">{MAIL_SVG}{EMAIL}</a>
    </div>
  </div>
</section>"""
    head = f'<script type="application/ld+json">{json.dumps(ORG_LD)}</script>'
    return layout(path="/index", title="DNNR Tech — AI Products & Startup Consulting in San Jose",
                  description="DNNR Tech is a San Jose, California technology company building AI-powered mobile apps and helping startups with product, mobile, and AI development.",
                  body=body, head_extra=head)


def page_services():
    steps = [
        ("Discovery call", "A short call to understand your product, users, and goals."),
        ("Scope & proposal", "A clear plan with milestones, deliverables, timeline, and cost."),
        ("Build & iterate", "Regular demos and shared progress, so you always see where things stand."),
        ("Launch & handoff", "Store submission, launch support, and documentation your team can own."),
    ]
    steps_html = "".join(f'<li><span class="step-n">{i+1:02d}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i, (t, d) in enumerate(steps))
    ai_apps = [a for a in APPS if a.get("ai")]
    proof = "".join(
        f'<a class="proof" href="/apps#{a["slug"]}"><img src="/static/apps/{a["slug"]}.png" alt="" width="40" height="40" loading="lazy"><span><b>{e(a["name"])}</b><em>{e(a["ai"])}</em></span></a>'
        for a in ai_apps
    )
    ld = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "DNNR Tech", "url": f"{SITE}/services",
          "email": EMAIL, "areaServed": "Worldwide", "address": ORG_LD["address"],
          "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Consulting services",
                              "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": sv["title"], "description": sv["summary"]}} for sv in SERVICES]}}
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>Consulting · {CITY}</span>
    <h1>Startup product &amp; AI consulting</h1>
    <p class="lead">We've designed, built, and launched {len(APPS)} apps of our own, {len(ai_apps)} of them with AI features. Now we help founders do the same, faster and with fewer surprises.</p>
    <div class="actions" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:28px">
      <a class="btn btn-ink" href="mailto:{EMAIL}?subject=Consulting%20inquiry">{MAIL_SVG}Start a conversation</a>
      <a class="btn btn-ghost" href="#process">How it works</a>
    </div>
  </div>
</div>

<section style="padding-top:32px">
  <div class="container">
    <div class="services services-full">{"".join(service_card(sv, full=True) for sv in SERVICES)}</div>
  </div>
</section>

<section style="padding-top:24px">
  <div class="container">
    <div class="section-head"><div><div class="rule"></div><h2 class="h2">Why DNNR Tech</h2></div></div>
    <div class="principles">
      <div class="principle"><div class="num">01</div><h3>We ship our own products</h3><p>{len(APPS)} apps live on the App Store and Google Play. We know what it takes to get from prototype to approved, updated, and used.</p></div>
      <div class="principle"><div class="num">02</div><h3>Hands-on AI experience</h3><p>Vision AI, LLM text generation, AI search, translation, content moderation, and on-device models, all running in production apps.</p></div>
      <div class="principle"><div class="num">03</div><h3>Based in Silicon Valley</h3><p>Headquartered in San Jose, California, and working remotely with teams anywhere.</p></div>
    </div>
  </div>
</section>

<section style="padding-top:24px">
  <div class="container">
    <div class="section-head"><div><div class="rule"></div><h2 class="h2">AI in our own apps</h2><p>Real features, in production today.</p></div></div>
    <div class="proofs">{proof}</div>
  </div>
</section>

<section id="process" style="padding-top:24px">
  <div class="container">
    <div class="section-head"><div><div class="rule"></div><h2 class="h2">How it works</h2></div></div>
    <ol class="steps">{steps_html}</ol>
  </div>
</section>

<section style="padding-top:16px">
  <div class="container">
    <div class="band">
      <div><h2>Tell us what you're building.</h2><p>Share your idea, stage, timeline, and budget. We'll reply with next steps.</p></div>
      <a class="btn" href="mailto:{EMAIL}?subject=Consulting%20inquiry">{MAIL_SVG}{EMAIL}</a>
    </div>
  </div>
</section>"""
    return layout(path="/services", title="Startup Product & AI Consulting", current="services",
                  description="AI product and MVP development, Flutter mobile app development, and AI integration advisory for startups, from a San Jose team that ships its own apps.",
                  body=body, head_extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>')


def page_apps():
    used = [c for c in REG["categories"] if any(a["category"] == c["id"] for a in APPS)]
    chips = '<button class="chip" type="button" data-filter="all" aria-pressed="true">All</button><button class="chip" type="button" data-filter="ai" aria-pressed="false">AI-powered</button>' + "".join(
        f'<button class="chip" type="button" data-filter="{c["id"]}" aria-pressed="false">{e(c["label"])}</button>' for c in used)
    ld = {
        "@context": "https://schema.org", "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {"@type": "MobileApplication", "name": a["name"], "description": a["tagline"],
                      "operatingSystem": "iOS, Android", "applicationCategory": CATS[a["category"]],
                      "url": f"{SITE}/apps#{a['slug']}", "image": f"{SITE}/static/apps/{a['slug']}.png",
                      "sameAs": [u for u in (ios_url(a), play_url(a)) if u],
                      "author": {"@type": "Organization", "name": "DNNR Tech"}}}
            for i, a in enumerate(APPS)
        ],
    }
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>{len(APPS)} apps · iOS &amp; Android</span>
    <h1>Our apps</h1>
    <p class="lead">Apps we design, build, and operate ourselves, {sum(1 for a in APPS if a.get("ai"))} of them with AI features. Every one is available on the App Store and Google Play.</p>
    <div class="stores" style="margin-top:22px">
      <a class="btn btn-ghost btn-sm" href="/ios">{APPLE_SVG}All on the App Store</a>
      <a class="btn btn-ghost btn-sm" href="/android">{PLAY_SVG}All on Google Play</a>
    </div>
  </div>
  <div class="chips" role="group" aria-label="Filter by category">{chips}</div>
  <div class="grid" id="app-grid" style="padding-bottom:96px">{"".join(app_card(a) for a in APPS)}</div>
</div>"""
    script = """<script>
  (function () {
    var chips = document.querySelectorAll('.chip');
    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        var f = c.dataset.filter;
        chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
        document.querySelectorAll('#app-grid .card').forEach(function (card) {
          card.hidden = f === 'ai' ? card.dataset.ai !== '1' : (f !== 'all' && card.dataset.cat !== f);
        });
      });
    });
  })();
</script>"""
    return layout(path="/apps", title="Apps", current="apps",
                  description=f"All {len(APPS)} DNNR Tech apps for iPhone and Android: TJ Near & Hot, What to Eat, AutoMiles, StampRescue, Golf Passport and more.",
                  body=body, head_extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>', scripts=script)


EN_LINK = ' · <a href="{path}">English</a>'


def page_privacy():
    en, ko = content("privacy_en.html"), content("privacy_ko.html")
    app_links = {a["slug"]: a for a in APPS}

    def expand(text):
        # {{app:slug}} -> icon + name for per-app <summary> rows
        return re.sub(r"\{\{app:([a-z0-9-]+)\}\}",
                      lambda m: f'<img src="/static/apps/{m.group(1)}.png" alt="" width="32" height="32">{e(app_links[m.group(1)]["name"])}', text)

    en, ko = expand(en), expand(ko)
    effective = content("privacy_date.txt").strip()
    en_page = doc_page(path="/privacy-policy", title="Privacy Policy", current="privacy",
                       description="How DNNR Tech apps collect, use, and protect your information, app by app.",
                       eyebrow="Legal", heading="Privacy Policy",
                       meta=f"Effective {effective} · Applies to all DNNR Tech apps",
                       body_html=en, toc=toc_from(en), extra_scripts=OPEN_DETAILS_SCRIPT)
    ko_page = doc_page(path="/ko/privacy-policy", title="개인정보처리방침", lang="ko",
                       description="DNNR Tech 앱의 개인정보 수집·이용·보호 방식과 앱별 상세 내용.",
                       eyebrow="Legal", heading="개인정보처리방침",
                       meta=f"시행일 {effective} · DNNR Tech의 모든 앱에 적용", alt_link=EN_LINK.format(path="/privacy-policy"),
                       body_html=ko, toc=toc_from(ko), extra_scripts=OPEN_DETAILS_SCRIPT)
    return en_page, ko_page


def page_support():
    en_page = doc_page(path="/support", title="Support", current="support",
                       description="Get help with DNNR Tech apps and request deletion of your data.",
                       eyebrow="Help center", heading="How can we help?",
                       meta="Support for every app published by DNNR Tech.", body_html=content("support_en.html"))
    ko_page = doc_page(path="/ko/support", title="고객 지원", lang="ko",
                       description="DNNR Tech 앱 고객 지원 및 데이터 삭제 요청 안내.",
                       eyebrow="Help center", heading="무엇을 도와드릴까요?",
                       meta="DNNR Tech의 모든 앱에 대한 지원 페이지입니다.", alt_link=EN_LINK.format(path="/support"),
                       body_html=content("support_ko.html"))
    return en_page, ko_page


def page_delete():
    en_page = doc_page(path="/delete-account", title="Data & Account Deletion",
                       description="How to delete your account and data in DNNR Tech apps.",
                       eyebrow="Your data", heading="Data &amp; account deletion",
                       meta="Applies to all apps published by DNNR Tech.", body_html=content("delete_en.html"))
    ko_page = doc_page(path="/ko/delete-account", title="데이터 및 계정 삭제", lang="ko",
                       description="DNNR Tech 앱의 계정 및 데이터 삭제 방법.",
                       eyebrow="Your data", heading="데이터 및 계정 삭제",
                       meta="DNNR Tech가 출시한 모든 앱에 적용됩니다.", alt_link=EN_LINK.format(path="/delete-account"),
                       body_html=content("delete_ko.html"))
    return en_page, ko_page


def page_academic_cv():
    a = next(x for x in APPS if x["slug"] == "academic-cv-ai")
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>App support</span>
    <div class="app-head" style="margin-top:20px"><img class="app-icon" src="/static/apps/{a['slug']}.png" alt="" width="60" height="60"><h1 style="margin:0">Academic CV AI Support</h1></div>
  </div>
  <div class="doc-layout single">
    <article class="prose">
      <p>We're here to help with questions, feedback, or problems with Academic CV AI.</p>
      <div class="callout">
        <p><strong>Report AI-generated content</strong><br>If the app produced inaccurate, offensive, or otherwise inappropriate content, please report it using the form below. Include what you asked for and what the app generated.</p>
        <p><a class="btn btn-ink" href="https://docs.google.com/forms/d/e/1FAIpQLSd93aXKlpX-oVZQFGrBTV-Up8HwOm6N-n3ETrGO8LjfgyNn2w/viewform?usp=dialog" rel="noopener">Submit a report or support request</a></p>
      </div>
      <p>You can also email <a href="mailto:{EMAIL}?subject=Academic%20CV%20AI">{EMAIL}</a>.</p>
      <p>See also: <a href="/support">DNNR Tech Support</a> · <a href="/privacy-policy#academic-cv-ai">Privacy details for Academic CV AI</a> · <a href="/delete-account">Data deletion</a></p>
      {store_buttons(a, "")}
    </article>
  </div>
</div>"""
    return layout(path="/academic_cv_support", title="Academic CV AI Support",
                  description="Support and AI content reporting for Academic CV AI.", body=body)


def page_404():
    body = f"""
<div class="container notfound">
  <div>
    <div class="code grad">404</div>
    <h1 class="h2" style="margin-top:12px">This page doesn't exist.</h1>
    <p class="lead" style="margin:14px auto 28px">The link may be old or mistyped. Try one of these instead.</p>
    <div class="stores" style="justify-content:center">
      <a class="btn btn-ink" href="/">Home</a><a class="btn btn-ghost" href="/apps">Our apps</a><a class="btn btn-ghost" href="/support">Support</a>
    </div>
  </div>
</div>"""
    return layout(path="/404", title="Page not found", description="Page not found.", body=body,
                  head_extra='<meta name="robots" content="noindex">')


def sitemap():
    paths = ["/", "/services", "/apps", "/support", "/delete-account", "/privacy-policy", "/academic_cv_support"]
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
        "privacy-policy.html": privacy_en,
        "support.html": support_en,
        "delete-account.html": delete_en,
        "ko/privacy-policy.html": privacy_ko,
        "ko/support.html": support_ko,
        "ko/delete-account.html": delete_ko,
        "academic_cv_support.html": page_academic_cv(),
        "404.html": page_404(),
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
