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

SITE = Path(__file__).resolve().parent.parent
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
GUIDES = json.loads((SITE / "data/guides.json").read_text(encoding="utf-8"))["guides"]
LANGS = ("fr", "en", "es")
e = html.escape

T = {
    "kicker": {"fr": "Studio indépendant · France", "en": "Independent studio · France", "es": "Estudio independiente · Francia"},
    "title": {"fr": "12 apps iPhone simples, qui gardent tes données sur ton téléphone.",
              "en": "12 simple iPhone apps that keep your data on your phone.",
              "es": "12 apps sencillas para iPhone que guardan tus datos en tu teléfono."},
    "sub": {"fr": "Cycle, course, hydratation, budget, Bourse, recettes, sommeil… Une app, une chose bien faite. Sans compte obligatoire.",
            "en": "Cycle, running, hydration, budget, stocks, recipes, sleep… One app, one thing done well. No account required.",
            "es": "Ciclo, correr, hidratación, presupuesto, bolsa, recetas, sueño… Una app, una cosa bien hecha. Sin cuenta obligatoria."},
    "cta_apps": {"fr": "Voir les 12 apps", "en": "See the 12 apps", "es": "Ver las 12 apps"},
    "cta_guides": {"fr": "Comparer avec Strava, Flo…", "en": "Compare with Strava, Flo…", "es": "Comparar con Strava, Flo…"},
    "proofs": {"fr": ["Sans compte obligatoire", "Données sur ton iPhone", "Téléchargement gratuit", "9 langues"],
               "en": ["No account required", "Data stays on your iPhone", "Free to download", "9 languages"],
               "es": ["Sin cuenta obligatoria", "Datos en tu iPhone", "Descarga gratuita", "9 idiomas"]},
    "guides_title": {"fr": "Quelle app choisir ?", "en": "Which app should you pick?", "es": "¿Qué app elegir?"},
    "guides_sub": {"fr": "Nos comparatifs honnêtes face aux apps les plus connues : prix, compte, données. Quand une autre app te convient mieux, on le dit.",
                   "en": "Honest comparisons with the best-known apps: price, account, data. When another app suits you better, we say so.",
                   "es": "Comparativas honestas con las apps más conocidas: precio, cuenta, datos. Si otra app te conviene más, lo decimos."},
    "guides_all": {"fr": "Tous les guides →", "en": "All guides →", "es": "Todas las guías →"},
    "why_title": {"fr": "Pourquoi nos apps", "en": "Why our apps", "es": "Por qué nuestras apps"},
    "why": {
        "fr": [("Aucun compte obligatoire", "Les 12 apps s'utilisent sans créer de compte. Tu ouvres, tu t'en sers."),
               ("Tes données restent chez toi", "Ton cycle, tes courses, tes dépenses… sont stockés sur ton iPhone, pas sur un serveur. Rien n'est revendu."),
               ("Prix affichés", "Gratuites au téléchargement. Le Premium optionnel est affiché en clair sur chaque page."),
               ("Pensées pour tout le monde", "9 langues, dont l'arabe de droite à gauche. Des apps sans jugement ni stéréotype.")],
        "en": [("No account required", "All 12 apps work without creating an account. Open it and go."),
               ("Your data stays with you", "Your cycle, runs, spending… are stored on your iPhone, not on a server. Nothing is sold."),
               ("Prices shown upfront", "Free to download. The optional Premium price is shown clearly on every page."),
               ("Built for everyone", "9 languages, including right-to-left Arabic. Apps with no judgment and no stereotypes.")],
        "es": [("Sin cuenta obligatoria", "Las 12 apps funcionan sin crear una cuenta. Abres y listo."),
               ("Tus datos se quedan contigo", "Tu ciclo, tus carreras, tus gastos… se guardan en tu iPhone, no en un servidor. Nada se vende."),
               ("Precios a la vista", "Descarga gratuita. El precio del Premium opcional aparece claro en cada página."),
               ("Pensadas para todos", "9 idiomas, incluido el árabe de derecha a izquierda. Apps sin juicios ni estereotipos.")],
    },
    "contact": {"fr": "Une question ? Écris-nous", "en": "A question? Write to us", "es": "¿Una pregunta? Escríbenos"},
    "res": {"fr": "Ressources", "en": "Resources", "es": "Recursos"},
    "res_links": {"fr": ["Guides comparatifs", "Contact & support", "Supprimer mon compte", "Mentions légales"],
                  "en": ["Comparison guides", "Contact & support", "Delete my account", "Legal notice"],
                  "es": ["Guías comparativas", "Contacto y soporte", "Eliminar mi cuenta", "Aviso legal"]},
}
GUIDE_SLUG_LANG = {"fr": "fr", "en": "en", "es": "es"}


def blocks(render):
    return "\n".join(render(l) for l in LANGS)


def hero():
    icons = "\n".join(
        f'          <a class="hero-apps__item" href="{a["slug"]}/" title="{e(a["name"])}">'
        f'<img src="assets/{a["slug"]}/icon-192.png" alt="{e(a["name"])}" width="56" height="56">'
        f'<span>{e(a["name"])}</span></a>' for a in APPS)

    def r(l):
        proofs = "".join(f"<li>{e(p)}</li>" for p in T["proofs"][l])
        return f"""        <div class="hero2__text" data-lang-block="{l}" lang="{l}">
          <p class="hero2__kicker">{e(T['kicker'][l])}</p>
          <h1 class="hero2__title">{e(T['title'][l])}</h1>
          <p class="hero2__sub">{e(T['sub'][l])}</p>
          <div class="hero2__ctas">
            <a class="hero2__btn hero2__btn--primary" href="#apps">{e(T['cta_apps'][l])}</a>
            <a class="hero2__btn" href="guides/">{e(T['cta_guides'][l])}</a>
          </div>
          <ul class="hero2__proofs">{proofs}</ul>
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


def guides():
    def r(l):
        cards = "\n".join(
            f'          <a class="guide-card" href="guides/{l}/{g["slug"][l]}/"><span class="guide-card__app">'
            f'{e(next(a["name"] for a in APPS if a["slug"] == g["app"]))}</span>'
            f'<span class="guide-card__title">{e(g["title"][l])}</span></a>' for g in GUIDES)
        return f"""      <div data-lang-block="{l}" lang="{l}">
        <h2 class="section-title">{e(T['guides_title'][l])}</h2>
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
    def r(l):
        items = "\n".join(f'          <div class="why__item"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in T["why"][l])
        return f"""      <div data-lang-block="{l}" lang="{l}">
        <h2 class="section-title">{e(T['why_title'][l])}</h2>
        <div class="why__grid">
{items}
        </div>
        <p class="why__contact"><a class="hero2__btn" href="contact.html">{e(T['contact'][l])}</a></p>
      </div>"""
    return f"""  <section class="why">
    <div class="container">
{blocks(r)}
    </div>
  </section>"""


def footer_col():
    hrefs = ["guides/", "contact.html", "suppression-compte.html", "mentions-legales.html"]

    def r(l):
        links = "".join(f'<a href="{h}">{e(t)}</a>' for h, t in zip(hrefs, T["res_links"][l]))
        return f'          <div data-lang-block="{l}" lang="{l}"><h4>{e(T["res"][l])}</h4>{links}</div>'
    return f"""        <div class="footer__col footer__col--res">
{blocks(r)}
        </div>"""


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
    s = put(s, "guides", guides(), r"  <section class=\"home-guides\">.*?</section>")
    s = put(s, "why", why(), r"  <section class=\"about-section\">.*?</section>")
    s = put(s, "footer-col", footer_col(),
            r"        <div class=\"footer__col\">\s*<h4 data-i18n=\"footer_legal\">.*?\n        </div>")
    p.write_text(s, encoding="utf-8")
    print("accueil régénéré")


if __name__ == "__main__":
    main()
