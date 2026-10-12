#!/usr/bin/env python3
"""Accueil : premier écran, guides, « pourquoi nos apps », pied de page.

Refonte du 2026-10-12. L'ancien accueil ne montrait aucune app au premier écran,
noyait les 12 apps dans des cartes géantes et alignait 24 liens légaux dans le
pied de page. Ce script régénère, entre marqueurs `<!-- home:<bloc>:start -->`,
les blocs `hero`, `guides`, `why` et `footer-col`, en FR / EN / ES statiques
(`data-lang-block`, comme les encadrés « En bref »). Aucune URL ne change :
les pages légales restent liées depuis chaque page d'app.

Idempotent. Source : data/apps.json, data/guides.json.
    python3 scripts/build_home.py
"""
import html
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_shell  # noqa: E402

SITE = Path(__file__).resolve().parent.parent
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
APPS_BY = {a["slug"]: a for a in APPS}
GUIDES = json.loads((SITE / "data/guides.json").read_text(encoding="utf-8"))["guides"]
LANGS = ("fr", "en", "es")
e = html.escape

T = {
    "kicker": {"fr": "Studio indépendant · France", "en": "Independent studio · France", "es": "Estudio independiente · Francia"},
    "title": {"fr": "Des apps simples, qui gardent tes données sur ton téléphone.",
              "en": "Simple apps that keep your data on your phone.",
              "es": "Apps sencillas que guardan tus datos en tu teléfono."},
    "sub": {"fr": "Cycle, course, hydratation, budget, Bourse, recettes, sommeil… Une app, une chose bien faite. Sans compte obligatoire.",
            "en": "Cycle, running, hydration, budget, stocks, recipes, sleep… One app, one thing done well. No account required.",
            "es": "Ciclo, correr, hidratación, presupuesto, bolsa, recetas, sueño… Una app, una cosa bien hecha. Sin cuenta obligatoria."},
    "cta_apps": {"fr": "Voir les 12 apps", "en": "See the 12 apps", "es": "Ver las 12 apps"},
    "cta_guides": {"fr": "Comparer avec Strava, Flo…", "en": "Compare with Strava, Flo…", "es": "Comparar con Strava, Flo…"},
    "stats": {"fr": [("12", "apps iPhone"), ("9", "langues"), ("0", "compte obligatoire"), ("0 €", "pour télécharger")],
              "en": [("12", "iPhone apps"), ("9", "languages"), ("0", "account required"), ("$0", "to download")],
              "es": [("12", "apps para iPhone"), ("9", "idiomas"), ("0", "cuentas obligatorias"), ("0 €", "para descargar")]},
    # Titres de section bicolores (première partie au dégradé du studio), façon wearebluefoxes.com
    "about_more": {"fr": "En savoir plus sur le studio", "en": "More about the studio", "es": "Más sobre el estudio"},
    "door_apps": {"fr": ["Nos", "apps"], "en": ["Our", "apps"], "es": ["Nuestras", "apps"]},
    "door_apps_text": {"fr": "12 apps, de la santé intime à la Bourse. Une app, un usage.", "en": "12 apps, from sexual health to the stock market. One app, one job.",
                       "es": "12 apps, de la salud íntima a la bolsa. Una app, un uso."},
    "door_apps_cta": {"fr": "Voir le catalogue", "en": "See the catalog", "es": "Ver el catálogo"},
    "door_guides": {"fr": ["Les", "guides"], "en": ["The", "guides"], "es": ["Las", "guías"]},
    "door_guides_text": {"fr": "Nos comparatifs honnêtes face à Strava, Flo, MyFitnessPal…", "en": "Our honest comparisons with Strava, Flo, MyFitnessPal…",
                         "es": "Nuestras comparativas honestas frente a Strava, Flo, MyFitnessPal…"},
    "door_guides_cta": {"fr": "Lire les guides", "en": "Read the guides", "es": "Leer las guías"},
    "door_ig": {"fr": ["Vu sur", "Instagram"], "en": ["Seen on", "Instagram"], "es": ["Visto en", "Instagram"]},
    "door_ig_text": {"fr": "Conseils et coulisses : les derniers posts de nos apps.", "en": "Tips and behind the scenes: the latest posts from our apps.",
                     "es": "Consejos y entre bastidores: las últimas publicaciones de nuestras apps."},
    "door_ig_cta": {"fr": "Voir les posts", "en": "See the posts", "es": "Ver las publicaciones"},
    "contact": {"fr": "Une question ? Écris-nous", "en": "A question? Write to us", "es": "¿Una pregunta? Escríbenos"},
}
GUIDE_SLUG_LANG = {"fr": "fr", "en": "en", "es": "es"}


def two_tone(parts):
    hl, rest = parts
    return f'<span class="tt-hl">{e(hl)}</span> {e(rest)}'


def blocks(render):
    return "\n".join(render(l) for l in LANGS)


def hero():
    icons = "\n".join(
        f'          <a class="hero-apps__item" href="{a["slug"]}/" data-app-link="{a["slug"]}" title="{e(a["name"])}">'
        f'<img src="assets/{a["slug"]}/icon-192.png" alt="{e(a["name"])}" width="56" height="56">'
        f'<span>{e(a["name"])}</span></a>' for a in APPS)

    def r(l):
        return f"""        <div class="hero2__text" data-lang-block="{l}" lang="{l}">
          <p class="hero2__kicker">{e(T['kicker'][l])}</p>
          <h1 class="hero2__title">{e(T['title'][l])}</h1>
          <p class="hero2__sub">{e(T['sub'][l])}</p>
          <div class="hero2__ctas">
            <a class="hero2__btn hero2__btn--primary" href="{site_shell.APPS_PAGE[l]}">{e(T['cta_apps'][l])}</a>
            <a class="hero2__btn" href="guides/">{e(T['cta_guides'][l])}</a>
          </div>
        </div>"""
    return f"""  <section class="studio-hero hero2">
    <div class="studio-hero__bg">
      <div class="stars"></div>
      <div class="orb orb--1"></div>
      <div class="orb orb--2"></div>
      <div class="orb orb--3"></div>
    </div>
    <div class="container hero2__inner">
{blocks(r)}
        <nav class="hero-apps" id="apps" aria-label="Apps">
{icons}
        </nav>
    </div>
  </section>"""


def stats():
    """Bande de chiffres sous le premier écran (idée reprise de wearebluefoxes.com).
    Uniquement des chiffres vérifiables : pas de téléchargements ni de notes."""
    def r(l):
        items = "".join(f'<div class="stats-band__item"><strong>{e(n)}</strong><span>{e(t)}</span></div>' for n, t in T["stats"][l])
        # La grille est dans un conteneur à part : le bloc de langue passe en display:block.
        return f'      <div data-lang-block="{l}" lang="{l}"><div class="stats-band__row">{items}</div></div>'
    return f"""  <section class="stats-band" aria-label="MyIdeApp">
    <div class="container">
{blocks(r)}
    </div>
  </section>"""



def why():
    """« POURQUOI MYIDEAPP ? » version courte : photo + titres des 4 valeurs, détail sur
    Qui sommes-nous (l'accueil reste une vitrine, sans doublon avec la page du studio)."""
    def r(l):
        vals = "\n".join(f'            <li>{e(t)}</li>' for t, _ in site_shell.VALUES[l])
        return f"""      <div data-lang-block="{l}" lang="{l}">
      <div class="split">
        <div class="split__media">{site_shell.photo("amis-cafe", l)}</div>
        <div class="split__text">
          <h2 class="section-title">{two_tone(site_shell.WHY_TITLE[l])}</h2>
          <ul class="values-short">
{vals}
          </ul>
          <p class="why__contact"><a class="hero2__btn" href="{site_shell.ABOUT[l]}">{e(T['about_more'][l])} →</a></p>
        </div>
      </div>
      </div>"""
    return f"""  <section class="why">
    <div class="container">
{blocks(r)}
    </div>
  </section>"""

def doors():
    """Trois portes d'entrée vers les pages du site, chacune avec un aperçu :
    Nos apps (icônes), Les guides (titres), Vu sur Instagram (dernier post)."""
    import build_instagram as IG
    path = SITE / "data/instagram.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"accounts": {}}
    last = IG.latest_per_account(data, 1)
    icons = "".join(f'<img src="assets/{a["slug"]}/icon-192.png" alt="" width="44" height="44" loading="lazy">' for a in APPS[:8])

    def r(l):
        guides = "".join(f'<span>{e(g["title"][l])}</span>' for g in GUIDES[:2])
        ig = ""
        if last:
            post, slug = last[0]
            ig = (f'<span class="door__post"><img src="{e(post["image"])}" alt="" loading="lazy">'
                  f'<span class="door__post-head"><img src="assets/{slug}/icon-192.png" alt="">@{e(APPS_BY[slug]["instagram"])}</span></span>')
        return f"""      <div data-lang-block="{l}" lang="{l}">
        <div class="doors">
          <a class="door" href="{site_shell.APPS_PAGE[l]}">
            <span class="door__preview door__preview--apps">{icons}</span>
            <span class="door__body"><strong class="door__title">{two_tone(T['door_apps'][l])}</strong>
            <span class="door__text">{e(T['door_apps_text'][l])}</span><span class="door__cta">{e(T['door_apps_cta'][l])} →</span></span>
          </a>
          <a class="door" href="guides/">
            <span class="door__preview door__preview--guides">{guides}</span>
            <span class="door__body"><strong class="door__title">{two_tone(T['door_guides'][l])}</strong>
            <span class="door__text">{e(T['door_guides_text'][l])}</span><span class="door__cta">{e(T['door_guides_cta'][l])} →</span></span>
          </a>
          <a class="door" href="{site_shell.IG_PAGE[l]}">
            <span class="door__preview door__preview--ig">{ig}</span>
            <span class="door__body"><strong class="door__title">{two_tone(T['door_ig'][l])}</strong>
            <span class="door__text">{e(T['door_ig_text'][l])}</span><span class="door__cta">{e(T['door_ig_cta'][l])} →</span></span>
          </a>
        </div>
      </div>"""
    return f"""  <section class="home-doors">
    <div class="container">
{blocks(r)}
    </div>
  </section>"""

def put(page, name, content, fallback_pattern):
    start, end = f"<!-- home:{name}:start -->", f"<!-- home:{name}:end -->"
    block = f"{start}\n{content}\n  {end}"
    if start in page:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, page, flags=re.S)
    m = re.search(fallback_pattern, page, flags=re.S)
    if not m:
        raise SystemExit(f"bloc {name} : point d'insertion introuvable")
    return page[:m.start()] + block + page[m.end():]


def main():
    p = SITE / "index.html"
    s = p.read_text(encoding="utf-8")
    s = put(s, "hero", hero(), r"  <section class=\"studio-hero\">.*?</section>")
    s = put(s, "stats", stats(), r"(?<=<!-- home:hero:end -->\n)")
    # Anciennes sections guides et Instagram : remplacées par les portes d'entrée.
    for old in ("instagram", "guides"):
        s = re.sub(r"<!-- home:" + old + r":start -->.*?<!-- home:" + old + r":end -->\n?", "", s, flags=re.S)
    s = put(s, "doors", doors(), r"(?<=<!-- home:stats:end -->\n)")
    s = put(s, "why", why(), r"  <section class=\"about-section\">.*?</section>")
    # Pied de page : habillage commun du studio (scripts/build_shell.py).
    p.write_text(s, encoding="utf-8")
    print("accueil régénéré")


if __name__ == "__main__":
    main()
