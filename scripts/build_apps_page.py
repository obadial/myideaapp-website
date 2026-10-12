#!/usr/bin/env python3
"""Page « Ce qu'on fait » : le catalogue des 12 apps, en vraies pages FR / EN / ES.

Pourquoi (2026-10-12) : « Ce qu'on fait » envoyait vers le milieu de l'accueil
(/#apps), qui empilait six blocs. Le catalogue (filtres + cartes) a sa page, comme
Guides, Qui sommes-nous et Instagram ; l'accueil redevient une vitrine courte.

Source : data/apps_catalog.html (français, clés i18n). Traduction avec les mêmes
règles que les pages d'app (scripts/build_lang_pages.py) : une clé manquante
fait échouer le script.

    /apps/   /en/apps/   /es/apps/
    python3 scripts/build_apps_page.py
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_guides as G  # noqa: E402
import build_lang_pages as L  # noqa: E402
import site_shell  # noqa: E402

SITE = G.SITE
BASE = G.BASE
LANGS = G.LANGS
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
e = html.escape

TXT = {
    "title": {"fr": "Nos apps : 12 apps simples, sans compte obligatoire | MyIdeApp",
              "en": "Our apps: 12 simple apps, no account required | MyIdeApp",
              "es": "Nuestras apps: 12 apps sencillas, sin cuenta obligatoria | MyIdeApp"},
    "desc": {"fr": "Les 12 apps du studio MyIdeApp : cycle, course, hydratation, budget, Bourse, recettes, sommeil, respiration… Tes données restent sur ton téléphone.",
             "en": "MyIdeApp's 12 apps: period tracking, running, hydration, budgeting, stocks, recipes, sleep, breathing… Your data stays on your phone.",
             "es": "Las 12 apps de MyIdeApp: ciclo, running, hidratación, presupuesto, bolsa, recetas, sueño, respiración… Tus datos se quedan en tu teléfono."},
    "h1": {"fr": ["Nos", "apps"], "en": ["Our", "apps"], "es": ["Nuestras", "apps"]},
    "intro": {"fr": "Une app, un usage, fait simplement. Gratuites au téléchargement, sans compte obligatoire, et tes données restent sur ton téléphone.",
              "en": "One app, one job, done simply. Free to download, no account required, and your data stays on your phone.",
              "es": "Una app, un uso, hecho con sencillez. Gratis, sin cuenta obligatoria, y tus datos se quedan en tu teléfono."},
    "crumb": {"fr": "Ce qu'on fait", "en": "What We Do", "es": "Lo que hacemos"},
    "compare": {"fr": "Tu hésites avec une autre app ? Lis nos comparatifs", "en": "Weighing up another app? Read our comparisons",
                "es": "¿Dudas con otra app? Lee nuestras comparativas"},
}

# Filtre par catégorie : quelques lignes autonomes (la page ne charge ni i18n.js ni main.js,
# qui changeraient la langue d'après le navigateur).
FILTER_JS = """  <script>
    document.querySelectorAll('.app-filter__btn').forEach(btn => btn.addEventListener('click', () => {
      document.querySelectorAll('.app-filter__btn').forEach(b => b.classList.toggle('active', b === btn));
      const f = btn.dataset.filter;
      document.querySelectorAll('.app-card[data-category]').forEach(card =>
        card.classList.toggle('is-filtered', f !== 'all' && card.dataset.category !== f));
    }));
  </script>"""


def two_tone(parts):
    hl, rest = parts
    return f'<span class="tt-hl">{e(hl)}</span> {e(rest)}'


def catalog(lang):
    src = (SITE / "data/apps_catalog.html").read_text(encoding="utf-8")
    src = re.sub(r"<!--.*?-->\n?", "", src, count=1, flags=re.S)
    if lang != "fr":
        src = L.translate(src, "catalogue", lang)
    # Liens et images depuis la racine ; la carte mène à la page de l'app dans la langue.
    src = re.sub(r'href="([a-z]+)/" data-app-link="\1"', lambda m: f'href="{L.url(m.group(1), lang)}"', src)
    src = src.replace('src="assets/', 'src="/assets/')
    return src


def page(lang):
    alternates = {l: BASE + site_shell.APPS_PAGE[l] for l in LANGS}
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": TXT["title"][lang], "url": BASE + site_shell.APPS_PAGE[lang],
           "inLanguage": lang, "isPartOf": {"@id": BASE + "/#organization"},
           "mainEntity": {"@type": "ItemList", "numberOfItems": len(APPS), "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "name": a["name"], "url": BASE + L.url(a["slug"], lang)}
               for i, a in enumerate(APPS)]}}]
    out = G.head(lang, TXT["title"][lang].replace(" | MyIdeApp", ""), TXT["desc"][lang], BASE + site_shell.APPS_PAGE[lang],
                 alternates, "studio", ld).replace('content="article"', 'content="website"', 1)
    body = f"""
  <main class="guide apps-page">
    <div class="container">
      <p class="guide__crumbs"><a href="/">MyIdeApp</a> › {e(TXT['crumb'][lang])}</p>
      <h1 class="guide__title">{two_tone(TXT['h1'][lang])}</h1>
      <p class="guide__intro">{e(TXT['intro'][lang])}</p>
      <section class="apps-section apps-section--page">
{catalog(lang)}
      </section>
      <p class="apps-page__compare"><a href="/guides/">{e(TXT['compare'][lang])} →</a></p>
    </div>
  </main>
"""
    return (out + "\n" + G.nav(lang, alternates, active="apps") + body + G.footer(lang)).replace(
        "\n</body>", "\n" + FILTER_JS + "\n</body>", 1)


def sitemap():
    p = SITE / "sitemap.xml"
    sm = p.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    entries = "\n".join(f"  <url>\n    <loc>{BASE}{site_shell.APPS_PAGE[l]}</loc>\n    <lastmod>{today}</lastmod>\n"
                        f"    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>" for l in LANGS)
    block = f"  <!-- apps-page:start -->\n{entries}\n  <!-- apps-page:end -->"
    if "<!-- apps-page:start -->" in sm:
        sm = re.sub(r"  <!-- apps-page:start -->.*?<!-- apps-page:end -->", lambda _: block, sm, flags=re.S)
    else:
        sm = sm.replace("</urlset>", block + "\n\n</urlset>")
    p.write_text(sm, encoding="utf-8")


def main():
    for lang in LANGS:
        out = SITE / site_shell.APPS_PAGE[lang].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang), encoding="utf-8")
    sitemap()
    print("Ce qu'on fait : 3 pages (catalogue des 12 apps), sitemap à jour")


if __name__ == "__main__":
    main()
