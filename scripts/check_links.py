#!/usr/bin/env python3
"""Garde-fou : aucune URL dont dépend un tiers ne doit casser.

Les apps (écrans légaux), les fiches App Store (support, marketing, privacy),
Google Play (suppression de compte) et AdMob (app-ads.txt) pointent sur ce site.
Une page renommée = un lien mort chez Apple ou Google, découvert au rejet suivant.

    python3 scripts/check_links.py          # vérifie les fichiers locaux (avant push)
    python3 scripts/check_links.py --live   # vérifie le site en ligne (après déploiement)

Sources des URL : la liste CRITICAL ci-dessous, toutes les URL myideapp.com trouvées
dans ../application (code Dart, ARB, plist, métadonnées fastlane), le sitemap, et
tous les liens internes des pages HTML. Code de sortie 1 si une URL est cassée.
"""
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, unquote

SITE = Path(__file__).resolve().parent.parent
APPS = SITE.parent / "application"

CRITICAL = [
    "https://myideapp.com/app-ads.txt",            # vérification AdMob
    "https://myideapp.com/suppression-compte.html",  # Google Play : suppression des données
    "https://myideapp.com/contact.html",           # support de Rhythm, EnjoyMeal, RunFree
    "https://myideapp.com/mentions-legales.html",
    "https://myideapp.com/robots.txt",
    "https://myideapp.com/sitemap.xml",
    "https://myideapp.com/llms.txt",
    "https://www.myideapp.com/nova/support",        # support Nova sur l'App Store
    "https://www.myideapp.com/nova/privacy",
    "https://www.myideapp.com/nova/terms",
    "https://myideapp.com/mycookbook/",            # ancienne URL de MyFoodBook
]
URL_RE = re.compile(r"https?://(?:www\.)?myideapp\.com[^\"'\s)<>|\\]*")


def collect() -> set[str]:
    urls = set(CRITICAL)
    if APPS.exists():
        for ext in ("*.dart", "*.arb", "*.plist", "*.txt", "*.json"):
            for f in APPS.rglob(ext):
                if any(p in f.parts for p in ("build", ".dart_tool", "Pods", "node_modules")):
                    continue
                try:
                    urls.update(URL_RE.findall(f.read_text(encoding="utf-8", errors="ignore")))
                except OSError:
                    pass
    urls.update(re.findall(r"<loc>([^<]+)</loc>", (SITE / "sitemap.xml").read_text(encoding="utf-8")))
    for page in SITE.rglob("*.html"):
        if {"scripts", "docs", "data"} & set(page.parts):
            continue
        rel = page.relative_to(SITE)
        for href in re.findall(r'\shref="([^"#:?]+)', page.read_text(encoding="utf-8")):
            if href.startswith(("http", "mailto", "//")) or href.endswith((".css", ".svg", ".png")):
                continue
            target = (Path("/") / rel.parent / href).resolve()
            urls.add("https://myideapp.com" + str(target) + ("/" if href.endswith("/") else ""))
    return {u.rstrip(".,;") for u in urls}


def local_ok(url: str) -> bool:
    """Résolution GitHub Pages : /x → x, x.html ou x/index.html."""
    path = unquote(urlparse(url).path).lstrip("/")
    base = SITE / path
    candidates = [base / "index.html"] if url.endswith("/") or not path else [base, Path(str(base) + ".html"), base / "index.html"]
    return any(c.is_file() for c in candidates)


def live_ok(url: str) -> bool:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "myideapp-linkcheck"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def malformed() -> list[str]:
    """Liens qu'aucune vérification d'URL ne voit : « // » sans domaine (lu par le
    navigateur comme une adresse vers un domaine vide, lien bloqué), href vide."""
    bad = []
    for page in SITE.rglob("*.html"):
        if {"scripts", "docs", "data"} & set(page.parts):
            continue
        for href in re.findall(r'\s(?:href|src)="([^"]*)"', page.read_text(encoding="utf-8")):
            if href == "" or re.match(r"^//(?![a-z0-9.-]+\.[a-z]{2,})", href, re.I):
                bad.append(f"{page.relative_to(SITE)} : lien mal formé « {href} »")
    return bad


def main():
    live = "--live" in sys.argv
    urls = sorted(collect())
    broken = [u for u in urls if not (live_ok(u) if live else local_ok(u))] + malformed()
    print(f"{len(urls)} URL vérifiées ({'en ligne' if live else 'fichiers locaux'}), {len(broken)} cassée(s)")
    for u in broken:
        print("  ✗", u)
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
