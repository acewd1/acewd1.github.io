#!/usr/bin/env python3
"""Notify IndexNow search engines (Bing, Yandex, Seznam, Naver...) about dnnr.us URLs.

    python3 _src/indexnow.py            # submit every URL in sitemap.xml
    python3 _src/indexnow.py /apps/foo  # submit specific paths

The key file /e26bcca08fd98b256e18fe73e1d7cd30.txt must stay deployed at the site root. Free API, no account needed.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = "https://dnnr.us"
KEY = "e26bcca08fd98b256e18fe73e1d7cd30"
ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) > 1:
        urls = [SITE + p if p.startswith("/") else p for p in sys.argv[1:]]
    else:
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        urls = [loc.text for loc in ET.parse(ROOT / "sitemap.xml").getroot().iter(ns + "loc")]
    body = json.dumps({"host": "dnnr.us", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")


if __name__ == "__main__":
    main()
