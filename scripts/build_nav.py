#!/usr/bin/env python3
"""Maillage entre pages d'app : lien vers le guide comparatif et vers les autres apps.

Avant, une page d'app était un cul-de-sac : seul « ← Studio » en sortait. Ce
script insère, juste avant le bloc anglais, un bloc `<!-- nav:start -->` …
`<!-- nav:end -->` avec le guide de l'app (dans la langue active) et les 11
autres apps (même thème d'abord), et ajoute un BreadcrumbList au JSON-LD.

Idempotent.
    python3 scripts/build_nav.py
"""
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = json.loads((SITE / "data" / "apps.json").read_text(encoding="utf-8"))
GUIDES = json.loads((SITE / "data" / "guides.json").read_text(encoding="utf-8"))["guides"]
CATS = DATA["categories"]
APPS = DATA["apps"]
START, END = "<!-- nav:start -->", "<!-- nav:end -->"
LANGS = ("fr", "en", "es")
LABEL = {
    "guide": {"fr": "Comparer {app} avec les alternatives", "en": "Compare {app} with alternatives", "es": "Comparar {app} con alternativas"},
    "others": {"fr": "Autres apps du studio", "en": "More apps from the studio", "es": "Más apps del estudio"},
}


def block(app):
    guide = next((g for g in GUIDES if g["app"] == app["slug"]), None)
    guide_links = ""
    if guide:
        guide_links = "\n".join(
            f'      <a class="app-crosslinks__guide" data-lang-block="{l}" href="/guides/{l}/{guide["slug"][l]}/">'
            f'{html.escape(LABEL["guide"][l].format(app=app["name"]))} →</a>' for l in LANGS)
    others = sorted((a for a in APPS if a["slug"] != app["slug"]),
                    key=lambda a: (a["category"] != app["category"], APPS.index(a)))
    chips = "\n".join(
        f'        <a href="../{a["slug"]}/"><img src="../assets/{a["slug"]}/icon-192.png" alt="" loading="lazy">{html.escape(a["name"])}</a>'
        for a in others)
    titles = "\n".join(f'      <h2 class="app-crosslinks__title" data-lang-block="{l}">{LABEL["others"][l]}</h2>' for l in LANGS)
    return f"""{START}
  <section class="app-crosslinks">
    <div class="container">
{guide_links}
{titles}
      <div class="app-crosslinks__list">
{chips}
      </div>
    </div>
  </section>
  {END}"""


def breadcrumb(app):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "MyIdeApp", "item": "https://myideapp.com/"},
        {"@type": "ListItem", "position": 2, "name": CATS[app["category"]]["en"], "item": "https://myideapp.com/#apps"},
        {"@type": "ListItem", "position": 3, "name": app["name"], "item": f"https://myideapp.com/{app['slug']}/"}]}


def main():
    for app in APPS:
        path = SITE / app["slug"] / "index.html"
        page = path.read_text(encoding="utf-8")
        b = block(app)
        if START in page:
            page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: b, page, flags=re.S)
        else:
            anchor = "<!-- llm-en:start -->" if "<!-- llm-en:start -->" in page else '  <footer class="footer">'
            page = page.replace(anchor, b + "\n\n  " + anchor.lstrip(), 1)
        page = re.sub(r'\n  <script type="application/ld\+json" data-nav>.*?</script>', "", page, flags=re.S)
        ld = json.dumps(breadcrumb(app), ensure_ascii=False, indent=2)
        page = page.replace("</head>", f'  <script type="application/ld+json" data-nav>\n{ld}\n  </script>\n</head>', 1)
        path.write_text(page, encoding="utf-8")
        print(f"ok {app['slug']}")


if __name__ == "__main__":
    main()
