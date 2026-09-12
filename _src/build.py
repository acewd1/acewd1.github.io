#!/usr/bin/env python3
"""Build dnnr.us static pages from _src/ into the repo root.

    python3 _src/build.py

Inputs:  _src/apps.json (app registry), _src/content/*.html (long-form copy)
Outputs: index.html, apps.html, privacy-policy.html, support.html,
         delete-account.html, academic_cv_support.html, 404.html,
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
      <article class="card" id="{a['slug']}" data-cat="{a['category']}">
        <div class="app-head">
          <img class="app-icon" src="/static/apps/{a['slug']}.png" alt="" width="60" height="60" loading="lazy">
          <div><h3>{e(a['name'])}</h3><div class="cat">{e(CATS[a['category']])}</div></div>
        </div>
        <p>{e(a['tagline'])}</p>
        {store_buttons(a)}
      </article>"""


def layout(*, path, title, description, body, current="", head_extra="", scripts=""):
    canonical = SITE + (path if path != "/index" else "/")
    full_title = title if title.startswith("DNNR Tech") else f"{title} — DNNR Tech"
    nav = [("/apps", "Apps", "apps", ""), ("/support", "Support", "support", "hide-sm"), ("/privacy-policy", "Privacy", "privacy", "hide-sm")]
    cur = ' aria-current="page"'
    nav_html = "".join(
        f'<a class="{cls}" href="{href}"{cur if key == current else ""}>{label}</a>'
        for href, label, key, cls in nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
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
        <p>Daily needs, naturally refined. Small, focused apps for everyday life.</p>
      </div>
      <div><b>Apps</b><a href="/apps">All apps</a><a href="/ios">iOS apps</a><a href="/android">Android apps</a></div>
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


LANG_SCRIPT = """<script>
  (function () {
    var q = new URLSearchParams(location.search).get('lang');
    var lang = q || ((navigator.language || '').toLowerCase().indexOf('ko') === 0 ? 'ko' : 'en');
    if (lang !== 'ko') lang = 'en';
    document.querySelectorAll('[data-lang]').forEach(function (el) { el.hidden = el.getAttribute('data-lang') !== lang; });
    document.querySelectorAll('.lang-switch a').forEach(function (a) { a.setAttribute('aria-current', a.dataset.to === lang ? 'true' : 'false'); });
    document.documentElement.lang = lang;
  })();
</script>"""


OPEN_DETAILS_SCRIPT = """<script>
  (function () {
    function open() {
      var el = location.hash && document.getElementById(location.hash.slice(1));
      if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
    }
    open(); window.addEventListener('hashchange', open);
  })();
</script>"""


def lang_switch():
    return '<div class="lang-switch" role="group" aria-label="Language"><a href="?lang=en" data-to="en" aria-current="true">English</a><a href="?lang=ko" data-to="ko" aria-current="false">한국어</a></div>'


def doc_page(*, path, title, description, eyebrow, heading_en, heading_ko, meta_en="", meta_ko="", en, ko, toc_en=None, toc_ko=None, current="", extra_scripts=""):
    def toc(items):
        if not items:
            return ""
        return '<nav class="toc" aria-label="On this page"><b>On this page</b>' + "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in items) + "</nav>"

    layout_cls = "doc-layout" if toc_en else "doc-layout single"
    body = f"""
<div class="container">
  <div class="doc-hero">
    <span class="eyebrow"><span class="dot"></span>{e(eyebrow)}</span>
    <h1 data-lang="en">{heading_en}</h1>
    <h1 data-lang="ko" hidden>{heading_ko}</h1>
    <p class="meta" data-lang="en">{meta_en}</p>
    <p class="meta" data-lang="ko" hidden>{meta_ko}</p>
    {lang_switch()}
  </div>
  <div class="{layout_cls}" data-lang="en">
    {toc(toc_en)}
    <article class="prose" lang="en">{en}</article>
  </div>
  <div class="{layout_cls}" data-lang="ko" hidden>
    {toc(toc_ko)}
    <article class="prose" lang="ko">{ko}</article>
  </div>
</div>"""
    return layout(path=path, title=title, description=description, body=body, current=current, scripts=LANG_SCRIPT + extra_scripts)


def content(name):
    return (SRC / "content" / name).read_text()


def toc_from(html_text):
    return re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', html_text)


# ---------------- pages ----------------

def page_home():
    featured = [a for a in APPS if a.get("featured")]
    mosaic = "".join(
        f'<a href="/apps#{a["slug"]}" title="{e(a["name"])}"><img src="/static/apps/{a["slug"]}.png" alt="{e(a["name"])}" width="128" height="128"></a>'
        for a in APPS[:12]
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "DNNR Tech",
        "url": SITE,
        "logo": f"{SITE}/static/icon-512.png",
        "email": EMAIL,
        "slogan": "Daily Needs, Naturally Refined",
        "sameAs": ["https://www.linkedin.com/company/dnnr-us/", "https://apps.apple.com/developer/id1668952055",
                   "https://play.google.com/store/apps/dev?id=6001862912587595419"],
    }
    body = f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow"><span class="dot"></span>Independent app studio</span>
      <h1 class="display">Daily needs,<br><span class="grad">naturally refined.</span></h1>
      <p class="lead">DNNR Tech builds small, focused apps for everyday moments — grocery runs, road trips, golf rounds, menus in a language you can't read, and the job hunt.</p>
      <div class="actions">
        <a class="btn btn-ink" href="/apps">Explore our apps</a>
        <a class="btn btn-ghost" href="mailto:{EMAIL}">{MAIL_SVG}Get in touch</a>
      </div>
      <div class="stats">
        <div><b>{len(APPS)}</b><span>apps released</span></div>
        <div><b>iOS &amp; Android</b><span>every app, both stores</span></div>
      </div>
    </div>
    <div class="mosaic" aria-hidden="true">{mosaic}</div>
  </div>
</section>

<section style="padding-top:32px">
  <div class="container">
    <div class="section-head">
      <div><div class="rule"></div><h2 class="h2">Featured apps</h2><p>A few of the apps people use every week.</p></div>
      <a class="btn btn-ghost" href="/apps">View all {len(APPS)} apps</a>
    </div>
    <div class="grid">{"".join(app_card(a) for a in featured)}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><div><div class="rule"></div><h2 class="h2">How we build</h2></div></div>
    <div class="principles">
      <div class="principle"><div class="num">01</div><h3>One job, done well</h3><p>Each app solves one everyday problem and gets you the answer in seconds, not menus.</p></div>
      <div class="principle"><div class="num">02</div><h3>Clear about your data</h3><p>We explain exactly what each app uses and why, and you can ask us to delete it anytime. <a href="/privacy-policy">Privacy policy</a></p></div>
      <div class="principle"><div class="num">03</div><h3>Always improving</h3><p>We ship updates often and read every message. Your feedback shapes what we build next.</p></div>
    </div>
  </div>
</section>

<section style="padding-top:16px">
  <div class="container">
    <div class="band">
      <div><h2>Questions, feedback, or partnerships?</h2><p>We usually reply within a few business days.</p></div>
      <a class="btn" href="mailto:{EMAIL}">{MAIL_SVG}{EMAIL}</a>
    </div>
  </div>
</section>"""
    head = f'<script type="application/ld+json">{json.dumps(ld)}</script>'
    return layout(path="/index", title="DNNR Tech — Daily Needs, Naturally Refined",
                  description="DNNR Tech is an independent studio building focused iOS and Android apps for everyday life.",
                  body=body, head_extra=head)


def page_apps():
    used = [c for c in REG["categories"] if any(a["category"] == c["id"] for a in APPS)]
    chips = '<button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
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
    <p class="lead">Every DNNR Tech app is available on the App Store and Google Play.</p>
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
          card.hidden = f !== 'all' && card.dataset.cat !== f;
        });
      });
    });
  })();
</script>"""
    return layout(path="/apps", title="Apps", current="apps",
                  description=f"All {len(APPS)} DNNR Tech apps for iPhone and Android: TJ Near & Hot, What to Eat, AutoMiles, StampRescue, Golf Passport and more.",
                  body=body, head_extra=f'<script type="application/ld+json">{json.dumps(ld)}</script>', scripts=script)


def page_privacy():
    en, ko = content("privacy_en.html"), content("privacy_ko.html")
    app_links = {a["slug"]: a for a in APPS}

    def expand(text):
        # {{app:slug}} -> icon + name for per-app <summary> rows
        return re.sub(r"\{\{app:([a-z0-9-]+)\}\}",
                      lambda m: f'<img src="/static/apps/{m.group(1)}.png" alt="" width="32" height="32">{e(app_links[m.group(1)]["name"])}', text)

    en, ko = expand(en), expand(ko)
    effective = content("privacy_date.txt").strip()
    return doc_page(path="/privacy-policy", title="Privacy Policy", current="privacy",
                    description="How DNNR Tech apps collect, use, and protect your information, app by app.",
                    eyebrow="Legal", heading_en="Privacy Policy", heading_ko="개인정보처리방침",
                    meta_en=f"Effective {effective} · Applies to all DNNR Tech apps",
                    meta_ko=f"시행일 {effective} · DNNR Tech의 모든 앱에 적용",
                    en=en, ko=ko, toc_en=toc_from(en), toc_ko=toc_from(ko), extra_scripts=OPEN_DETAILS_SCRIPT)


def page_support():
    return doc_page(path="/support", title="Support", current="support",
                    description="Get help with DNNR Tech apps and request deletion of your data.",
                    eyebrow="Help center", heading_en="How can we help?", heading_ko="무엇을 도와드릴까요?",
                    meta_en="Support for every app published by DNNR Tech.", meta_ko="DNNR Tech의 모든 앱에 대한 지원 페이지입니다.",
                    en=content("support_en.html"), ko=content("support_ko.html"))


def page_delete():
    return doc_page(path="/delete-account", title="Data & Account Deletion",
                    description="How to delete your account and data in DNNR Tech apps.",
                    eyebrow="Your data", heading_en="Data &amp; account deletion", heading_ko="데이터 및 계정 삭제",
                    meta_en="Applies to all apps published by DNNR Tech.", meta_ko="DNNR Tech가 출시한 모든 앱에 적용됩니다.",
                    en=content("delete_en.html"), ko=content("delete_ko.html"))


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
    paths = ["/", "/apps", "/support", "/delete-account", "/privacy-policy", "/academic_cv_support"]
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def main():
    pages = {
        "index.html": page_home(),
        "apps.html": page_apps(),
        "privacy-policy.html": page_privacy(),
        "support.html": page_support(),
        "delete-account.html": page_delete(),
        "academic_cv_support.html": page_academic_cv(),
        "404.html": page_404(),
        "sitemap.xml": sitemap(),
        "robots.txt": f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
    }
    for name, text in pages.items():
        (ROOT / name).write_text(text)
    missing = [a["slug"] for a in APPS if not (ROOT / "static" / "apps" / f"{a['slug']}.png").exists()]
    if missing:
        raise SystemExit(f"Missing icons in static/apps/: {missing}")
    print(f"Built {len(pages)} files for {len(APPS)} apps.")


if __name__ == "__main__":
    main()
