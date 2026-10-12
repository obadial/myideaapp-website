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
    "guides_title": {"fr": ("Quelle app", "choisir ?"), "en": ("Which app", "should you pick?"), "es": ("¿Qué app", "elegir?")},
    "guides_sub": {"fr": "Nos comparatifs honnêtes face aux apps les plus connues : prix, compte, données. Quand une autre app te convient mieux, on le dit.",
                   "en": "Honest comparisons with the best-known apps: price, account, data. When another app suits you better, we say so.",
                   "es": "Comparativas honestas con las apps más conocidas: precio, cuenta, datos. Si otra app te conviene más, lo decimos."},
    "guides_all": {"fr": "Tous les guides →", "en": "All guides →", "es": "Todas las guías →"},
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
            <a class="hero2__btn hero2__btn--primary" href="#apps">{e(T['cta_apps'][l])}</a>
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
        <nav class="hero-apps" aria-label="Apps">
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


def guides():
    def r(l):
        cards = "\n".join(
            f'          <a class="guide-card" href="guides/{l}/{g["slug"][l]}/"><span class="guide-card__app">'
            f'{e(next(a["name"] for a in APPS if a["slug"] == g["app"]))}</span>'
            f'<span class="guide-card__title">{e(g["title"][l])}</span></a>' for g in GUIDES)
        return f"""      <div data-lang-block="{l}" lang="{l}">
        <h2 class="section-title">{two_tone(T['guides_title'][l])}</h2>
        <p class="section-subtitle">{e(T['guides_sub'][l])}</p>
        <div class="guide-grid">
{cards}
        </div>
        <p class="home-guides__all"><a href="guides/">{e(T['guides_all'][l])}</a></p>
      </div>"""
    return f"""  <section class="home-guides">
    <div class="container">
{blocks(r)}
    </div>
  </section>"""


def why():
    """« POURQUOI MYIDEAPP ? » : photo à gauche, valeurs à droite (structure wearebluefoxes.com).
    Valeurs et photos partagées avec la page À propos (scripts/site_shell.py)."""
    def r(l):
        return f"""      <div data-lang-block="{l}" lang="{l}">
      <div class="split">
        <div class="split__media">{site_shell.photo("amis-cafe", l)}</div>
        <div class="split__text">
          <h2 class="section-title">{two_tone(site_shell.WHY_TITLE[l])}</h2>
          <div class="values">
{site_shell.values_list(l)}
          </div>
          <p class="why__contact"><a class="hero2__btn" href="contact.html">{e(T['contact'][l])}</a></p>
        </div>
      </div>
      </div>"""
    return f"""  <section class="why">
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
    s = put(s, "guides", guides(), r"  <section class=\"home-guides\">.*?</section>")
    s = put(s, "why", why(), r"  <section class=\"about-section\">.*?</section>")
    # Pied de page : habillage commun du studio (scripts/build_shell.py).
    p.write_text(s, encoding="utf-8")
    print("accueil régénéré")


if __name__ == "__main__":
    main()
