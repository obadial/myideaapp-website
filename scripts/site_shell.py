"""Habillage commun du site : barre de navigation et pied de page du studio.

Pourquoi (2026-10-12) : Contact, Suppression de compte et Mentions légales
n'avaient ni menu ni vrai pied de page (le visiteur avait l'impression de
quitter le site), et chaque page avait son propre pied de page. Inspiré de la
structure de wearebluefoxes.com : même en-tête et même pied de page partout,
pied de page en 4 zones (studio · une question ? · réseaux · ressources).

Pas d'adresse postale ni d'autre donnée personnelle (choix de Lucas).
Les pages d'app gardent leur barre et leur pied de page à leurs couleurs.

Deux variantes :
- `footer(lang)` / `nav(lang, …)` pour les pages générées dans une langue fixe
  (guides, À propos) ;
- `footer_multi()` / `nav_multi()` pour les pages traduites par js/i18n.js
  (accueil, Contact, Suppression de compte, Mentions légales) : le pied de page
  porte les 3 langues en blocs `data-lang-block`.
Appliqué par build_guides.py, build_about.py et build_shell.py.
"""
import html
import json
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
LANGS = ("fr", "en", "es")
EMAIL = "contact.myideapp@icloud.com"
ABOUT = {"fr": "/a-propos/", "en": "/en/about/", "es": "/es/acerca-de/"}
e = html.escape

T = {
    "tagline": {"fr": "Studio indépendant d'apps iPhone. 12 apps simples, tes données sur ton téléphone.",
                "en": "Independent iPhone app studio. 12 simple apps, your data on your phone.",
                "es": "Estudio independiente de apps para iPhone. 12 apps sencillas, tus datos en tu teléfono."},
    "question": {"fr": "Une question ?", "en": "A question?", "es": "¿Una pregunta?"},
    "form": {"fr": "Formulaire de contact", "en": "Contact form", "es": "Formulario de contacto"},
    "reply": {"fr": "Réponse sous 48 h", "en": "Reply within 48 hours", "es": "Respuesta en 48 h"},
    "insta": {"fr": "Nos apps sur Instagram", "en": "Our apps on Instagram", "es": "Nuestras apps en Instagram"},
    "res": {"fr": "Ressources", "en": "Resources", "es": "Recursos"},
    "guides": {"fr": "Guides comparatifs", "en": "Comparison guides", "es": "Guías comparativas"},
    "about": {"fr": "À propos du studio", "en": "About the studio", "es": "Sobre el estudio"},
    "delete": {"fr": "Supprimer mon compte", "en": "Delete my account", "es": "Eliminar mi cuenta"},
    "legal": {"fr": "Mentions légales", "en": "Legal notice", "es": "Aviso legal"},
    "rights": {"fr": "© 2026 MyIdeApp. Tous droits réservés.", "en": "© 2026 MyIdeApp. All rights reserved.",
               "es": "© 2026 MyIdeApp. Todos los derechos reservados."},
    "made": {"fr": "Conçu en France", "en": "Made in France", "es": "Hecho en Francia"},
}


def instagram_links():
    return "".join(
        f'<a class="site-footer__ig" href="https://www.instagram.com/{a["instagram"]}/" rel="noopener" target="_blank">'
        f'<img src="/assets/{a["slug"]}/icon-192.png" alt="" width="20" height="20" loading="lazy">{e(a["name"])}</a>'
        for a in APPS if a.get("instagram"))


def footer_inner(lang):
    return f"""      <div class="site-footer__grid">
        <div class="site-footer__brand">
          <a href="/" class="logo-text">MyIdeApp</a>
          <p>{e(T['tagline'][lang])}</p>
        </div>
        <div class="site-footer__col">
          <h4>{e(T['question'][lang])}</h4>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <a href="/contact.html">{e(T['form'][lang])}</a>
          <span class="site-footer__note">{e(T['reply'][lang])}</span>
        </div>
        <div class="site-footer__col site-footer__col--ig">
          <h4>{e(T['insta'][lang])}</h4>
          <div class="site-footer__igs">{instagram_links()}</div>
        </div>
        <div class="site-footer__col">
          <h4>{e(T['res'][lang])}</h4>
          <a href="/guides/">{e(T['guides'][lang])}</a>
          <a href="{ABOUT[lang]}">{e(T['about'][lang])}</a>
          <a href="/suppression-compte.html">{e(T['delete'][lang])}</a>
          <a href="/mentions-legales.html">{e(T['legal'][lang])}</a>
        </div>
      </div>
      <div class="footer__bottom">
        <p>{e(T['rights'][lang])}</p>
        <p>{e(T['made'][lang])}</p>
      </div>"""


def footer(lang):
    return f"""  <footer class="footer site-footer">
    <div class="container">
{footer_inner(lang)}
    </div>
  </footer>"""


def footer_multi():
    blocks = "\n".join(f'    <div class="container" data-lang-block="{l}" lang="{l}">\n{footer_inner(l)}\n    </div>' for l in LANGS)
    return f'  <footer class="footer site-footer">\n{blocks}\n  </footer>'


NAV_LABELS = {"apps": {"fr": "Apps", "en": "Apps", "es": "Apps"},
              "guides": {"fr": "Guides", "en": "Guides", "es": "Guías"},
              "about": {"fr": "À propos", "en": "About", "es": "Acerca de"},
              "contact": {"fr": "Contact", "en": "Contact", "es": "Contacto"}}


def nav_multi(active=None):
    """Barre du studio pour les pages traduites par i18n.js (boutons de langue)."""
    def cls(name):
        return ' class="active"' if name == active else ""
    return f"""  <nav class="navbar guide-nav">
    <div class="navbar__left"><a href="/" class="logo-text guide-nav__logo">MyIdeApp</a></div>
    <div class="navbar__nav guide-nav__links">
      <a href="/#apps" data-i18n="nav_apps"{cls('apps')}>Apps</a>
      <a href="/guides/" data-i18n="nav_guides"{cls('guides')}>Guides</a>
      <a href="/a-propos/" data-i18n="nav_about" data-i18n-href="nav_about_href"{cls('about')}>À propos</a>
      <a href="/contact.html" data-i18n="nav_contact"{cls('contact')}>Contact</a>
    </div>
    <div class="navbar__right">
      <div class="lang-switcher">
        <button class="lang-btn" data-lang-btn="fr">FR</button>
        <button class="lang-btn" data-lang-btn="en">EN</button>
        <button class="lang-btn" data-lang-btn="es">ES</button>
      </div>
    </div>
  </nav>"""
