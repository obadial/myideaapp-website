#!/usr/bin/env python3
"""Pages « réponses » (GEO) : comparatifs honnêtes, en vraies pages FR / EN / ES.

Source : data/guides.json (contenu, sources des concurrents) + data/apps.json
(nos prix). Une page par guide et par langue, sans i18n.js : chaque page porte
sa langue en dur, et les trois versions se référencent par hreflang.

    /guides/                       hub (3 langues en blocs, langue choisie par i18n.js)
    /guides/<lang>/<slug>/         un guide

Idempotent. Met aussi à jour le bloc `guides` du sitemap.
    python3 scripts/build_guides.py
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_shell  # noqa: E402

SITE = Path(__file__).resolve().parent.parent
BASE = "https://myideapp.com"
G = json.loads((SITE / "data" / "guides.json").read_text(encoding="utf-8"))
APPS = {a["slug"]: a for a in json.loads((SITE / "data" / "apps.json").read_text(encoding="utf-8"))["apps"]}
UI = G["ui"]
LANGS = ("fr", "en", "es")
THEMES = set(re.findall(r'\[data-theme="([a-z]+)"\]', (SITE / "css" / "style.css").read_text(encoding="utf-8")))
MONTHS = {
    "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(),
    "en": "January February March April May June July August September October November December".split(),
    "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(),
}
e = html.escape
ABOUT = {"fr": "/a-propos/", "en": "/en/about/", "es": "/es/acerca-de/"}
ABOUT_LABEL = {"fr": "À propos", "en": "About", "es": "Acerca de"}


def human_date(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    mo = MONTHS[lang][m - 1]
    return {"fr": f"{d} {mo} {y}", "en": f"{mo} {d}, {y}", "es": f"{d} de {mo} de {y}"}[lang]


def price(app, lang):
    p = app["price"]
    if not app.get("premium_available", True):
        return {"fr": "Gratuit (Premium bientôt)", "en": "Free (Premium coming soon)",
                "es": "Gratis (Premium próximamente)"}[lang]
    return {"fr": f"Gratuit, Premium {p['monthly_eur']} €/mois ou {p['annual_eur']} €/an",
            "en": f"Free, Premium ${p['monthly_usd']}/month or ${p['annual_usd']}/year",
            "es": f"Gratis, Premium {p['monthly_eur']} €/mes o {p['annual_eur']} €/año"}[lang]


def url(guide, lang):
    return f"{BASE}/guides/{lang}/{guide['slug'][lang]}/"


def app_path(slug, lang):
    """Page de l'app dans la langue du guide (/rhythm/, /en/rhythm/, /es/rhythm/)."""
    return f"/{slug}/" if lang == "fr" else f"/{lang}/{slug}/"


def store_url(slug):
    page = (SITE / slug / "index.html").read_text(encoding="utf-8")
    m = re.search(r'"downloadUrl":\s*"([^"]+)"', page)
    return m.group(1) if m else f"{BASE}/{slug}/"


def head(lang, title, desc, canonical, alternates, theme, extra_ld):
    alt = "\n".join(f'  <link rel="alternate" hreflang="{l}" href="{u}">' for l, u in alternates.items())
    if "en" in alternates:
        alt += f'\n  <link rel="alternate" hreflang="x-default" href="{alternates["en"]}">'
    ld = "\n".join(f'  <script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n  </script>' for x in extra_ld)
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="{theme}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)} | MyIdeApp</title>
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="index, follow">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE}/assets/og-studio.png">
  <link rel="canonical" href="{canonical}">
{alt}
  <link rel="stylesheet" href="/css/fonts.css">
  <link rel="stylesheet" href="/css/style.css">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
{ld}
</head>"""


def nav(lang, lang_links):
    links = " ".join(
        f'<a class="lang-btn{" active" if l == lang else ""}" href="{u}" hreflang="{l}">{l.upper()}</a>'
        for l, u in lang_links.items())
    return f"""<body data-theme="studio">
  <nav class="navbar guide-nav">
    <div class="navbar__left"><a href="/" class="logo-text guide-nav__logo">MyIdeApp</a></div>
    <div class="navbar__nav guide-nav__links">
      <a href="/#apps">Apps</a>
      <a href="/guides/">{e(UI['guides'][lang])}</a>
      <a href="{ABOUT[lang]}">{ABOUT_LABEL[lang]}</a>
      <a href="/contact.html">Contact</a>
    </div>
    <div class="navbar__right"><div class="lang-switcher">{links}</div></div>
  </nav>"""


def footer(lang):
    """Pied de page commun du studio (scripts/site_shell.py), dans la langue de la page."""
    return site_shell.footer(lang) + "\n</body>\n</html>\n"


def comp_name(guide, name, lang):
    return guide.get("competitor_names", {}).get(name, {}).get(lang, name)


def guide_page(guide, lang):
    app = APPS[guide["app"]]
    name = app["name"]
    checked = G["_meta"]["checked"]
    canonical = url(guide, lang)
    alternates = {l: url(guide, l) for l in LANGS}
    cols = [name] + [comp_name(guide, c, lang) for c in guide["competitors"]]

    def cell(v):
        return price(app, lang) if v == "__PRICE__" else v[lang]

    thead = "".join(f'<th scope="col"{" class=guide-table__ours" if i == 0 else ""}>{e(c)}</th>' for i, c in enumerate(cols))
    tbody = "\n".join(
        f'          <tr><th scope="row">{e(r["label"][lang])}</th><td class="guide-table__ours">{e(cell(r["ours"]))}</td>'
        + "".join(f"<td>{e(t[lang])}</td>" for t in r["them"]) + "</tr>"
        for r in guide["rows"])
    why = "\n".join(f"          <li>{e(x)}</li>" for x in guide["why"][lang])
    faq_html = "\n".join(
        f'        <details class="faq-item"><summary>{e(f["q"][lang])}</summary><p>{e(f["a"][lang])}</p></details>'
        for f in guide["faq"])
    sources = "\n".join(f'          <li><a href="{e(s["url"])}" rel="nofollow noopener" target="_blank">{e(s["label"])}</a></li>'
                        for s in guide["sources"])
    other = " · ".join(f'<a href="{alternates[l]}" hreflang="{l}">{l.upper()}</a>' for l in LANGS if l != lang)

    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": guide["title"][lang],
         "description": guide["description"][lang], "inLanguage": lang, "mainEntityOfPage": canonical,
         "datePublished": checked, "dateModified": checked,
         "author": {"@type": "Organization", "name": "MyIdeApp", "url": BASE + "/"},
         "publisher": {"@type": "Organization", "name": "MyIdeApp", "url": BASE + "/"},
         "about": {"@type": "SoftwareApplication", "name": name, "operatingSystem": "iOS",
                   "url": f"{BASE}{app_path(guide['app'], lang)}"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"][lang], "acceptedAnswer": {"@type": "Answer", "text": f["a"][lang]}}
            for f in guide["faq"]]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": UI["home"][lang], "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": UI["guides"][lang], "item": BASE + "/guides/"},
            {"@type": "ListItem", "position": 3, "name": guide["title"][lang], "item": canonical}]},
    ]
    theme = guide["app"] if guide["app"] in THEMES else "studio"
    # <title> court (≤ 60 car.) pour Google ; le titre long reste le h1 de la page.
    return (head(lang, guide["seo_title"][lang], guide["description"][lang], canonical, alternates, theme, ld)
            + "\n" + nav(lang, alternates).replace('data-theme="studio"', f'data-theme="{theme}"') + f"""
  <main class="guide">
    <div class="container guide__container">
      <nav class="guide__crumbs" aria-label="breadcrumb"><a href="/">{e(UI['home'][lang])}</a> › <a href="/guides/">{e(UI['guides'][lang])}</a></nav>
      <h1 class="guide__title">{e(guide['title'][lang])}</h1>
      <p class="guide__by">{e(UI['by'][lang].format(app=name))} {e(UI['other_langs'][lang])} {other}</p>

      <section class="guide__answer">
        <h2>{e(UI['short_answer'][lang])}</h2>
        <p>{e(guide['answer'][lang])}</p>
      </section>

      <section>
        <h2>{e(UI['comparison'][lang])}</h2>
        <div class="guide-table__wrap">
        <table class="guide-table">
          <thead><tr><th scope="col">{e(UI['criterion'][lang])}</th>{thead}</tr></thead>
          <tbody>
{tbody}
          </tbody>
        </table>
        </div>
      </section>

      <section>
        <h2>{e(UI['why'][lang].format(app=name))}</h2>
        <ul class="guide__list">
{why}
        </ul>
        <p class="guide__cta">
          <a class="btn-store" href="{store_url(guide['app'])}">{e(UI['cta'][lang].format(app=name))}</a>
          <a class="guide__more" href="{app_path(guide['app'], lang)}">{e(UI['more'][lang].format(app=name))} →</a>
        </p>
      </section>

      <section>
        <h2>{e(UI['when_other'][lang])}</h2>
        <p>{e(guide['when_other'][lang])}</p>
      </section>

      <section class="faq">
        <h2>{e(UI['faq'][lang])}</h2>
{faq_html}
      </section>

      <section class="guide__sources">
        <h2>{e(UI['sources'][lang])}</h2>
        <ul>
{sources}
        </ul>
        <p class="guide__checked">{e(UI['checked'][lang].format(d=human_date(checked, lang)))}</p>
      </section>
    </div>
  </main>
""" + footer(lang))


def hub():
    blocks = []
    for lang in LANGS:
        cards = "\n".join(
            f'        <a class="guide-card" href="{url(g, lang)}"><span class="guide-card__app">{e(APPS[g["app"]]["name"])}</span>'
            f'<span class="guide-card__title">{e(g["title"][lang])}</span><span class="guide-card__desc">{e(g["description"][lang])}</span></a>'
            for g in G["guides"])
        blocks.append(f"""      <div data-lang-block="{lang}" lang="{lang}">
        <h1 class="guide__title">{e(G['hub']['title'][lang])}</h1>
        <p class="guide__by">{e(G['hub']['intro'][lang])}</p>
        <div class="guide-grid">
{cards}
        </div>
      </div>""")
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": G["hub"]["title"]["en"],
           "url": BASE + "/guides/", "hasPart": [{"@type": "Article", "headline": g["title"]["en"], "url": url(g, "en")}
                                                for g in G["guides"]]}]
    page = head("fr", G["hub"]["title"]["fr"], "Comparatifs honnêtes de nos apps face à Strava, Flo, Clue, MyFitnessPal… : prix, compte obligatoire, données.", BASE + "/guides/", {}, "studio", ld)
    page = page.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
    page = page.replace("<title>", '<title data-i18n="guides_hub_title">', 1)
    return page + f"""
<body data-theme="studio">
  <nav class="navbar guide-nav">
    <div class="navbar__left"><a href="/" class="logo-text guide-nav__logo">MyIdeApp</a></div>
    <div class="navbar__nav guide-nav__links">
      <a href="/#apps">Apps</a>
      <a href="/guides/" class="active">Guides</a>
      <a href="/a-propos/" data-i18n="nav_about" data-i18n-href="nav_about_href">À propos</a>
      <a href="/contact.html">Contact</a>
    </div>
    <div class="navbar__right">
      <div class="lang-switcher">
        <button class="lang-btn" data-lang-btn="fr">FR</button>
        <button class="lang-btn" data-lang-btn="en">EN</button>
        <button class="lang-btn" data-lang-btn="es">ES</button>
      </div>
    </div>
  </nav>
  <main class="guide">
    <div class="container guide__container">
{chr(10).join(blocks)}
    </div>
  </main>
""" + site_shell.footer_multi() + '\n  <script src="/js/i18n.js"></script>\n  <script>document.addEventListener("DOMContentLoaded", () => I18n.init());</script>\n</body>\n</html>\n'


def update_sitemap(urls):
    path = SITE / "sitemap.xml"
    sm = path.read_text(encoding="utf-8")
    sm = re.sub(r"\n  <!-- guides:start -->.*?<!-- guides:end -->", "", sm, flags=re.S)
    entries = "".join(
        f"\n  <url>\n    <loc>{u}</loc>\n    <lastmod>{G['_meta']['checked']}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
        for u, pr in urls)
    sm = sm.replace("</urlset>", f"  <!-- guides:start -->{entries}\n  <!-- guides:end -->\n</urlset>")
    path.write_text(sm, encoding="utf-8")


def main():
    out = SITE / "guides"
    for lang in LANGS:
        if (out / lang).exists():
            shutil.rmtree(out / lang)
    urls = [(BASE + "/guides/", "0.8")]
    for g in G["guides"]:
        for lang in LANGS:
            d = out / lang / g["slug"][lang]
            d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(guide_page(g, lang), encoding="utf-8")
            urls.append((url(g, lang), "0.8"))
    (out / "index.html").write_text(hub(), encoding="utf-8")
    update_sitemap(urls)
    print(f"{len(G['guides'])} guides × {len(LANGS)} langues + hub, sitemap à jour ({len(urls)} URL)")


if __name__ == "__main__":
    main()
