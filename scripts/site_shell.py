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
IG_PAGE = {"fr": "/instagram/", "en": "/en/instagram/", "es": "/es/instagram/"}
APPS_PAGE = {"fr": "/apps/", "en": "/en/apps/", "es": "/es/apps/"}
e = html.escape

T = {
    "tagline": {"fr": "Studio indépendant d'apps mobiles. Des apps simples, tes données sur ton téléphone.",
                "en": "Independent mobile app studio. Simple apps, your data on your phone.",
                "es": "Estudio independiente de apps móviles. Apps sencillas, tus datos en tu teléfono."},
    "question": {"fr": "Une question ?", "en": "A question?", "es": "¿Una pregunta?"},
    "form": {"fr": "Formulaire de contact", "en": "Contact form", "es": "Formulario de contacto"},
    "reply": {"fr": "Réponse sous 48 h", "en": "Reply within 48 hours", "es": "Respuesta en 48 h"},
    "insta": {"fr": "Nos apps sur Instagram", "en": "Our apps on Instagram", "es": "Nuestras apps en Instagram"},
    "ig_all": {"fr": "Voir leurs derniers posts", "en": "See their latest posts", "es": "Ver sus últimas publicaciones"},
    "res": {"fr": "Ressources", "en": "Resources", "es": "Recursos"},
    "all_apps": {"fr": "Nos 12 apps", "en": "Our 12 apps", "es": "Nuestras 12 apps"},
    "guides": {"fr": "Guides comparatifs", "en": "Comparison guides", "es": "Guías comparativas"},
    "about": {"fr": "Qui sommes-nous", "en": "Who We Are", "es": "Quiénes somos"},
    "delete": {"fr": "Supprimer mon compte", "en": "Delete my account", "es": "Eliminar mi cuenta"},
    "legal": {"fr": "Mentions légales", "en": "Legal notice", "es": "Aviso legal"},
    "rights": {"fr": "© 2026 MyIdeApp. Tous droits réservés.", "en": "© 2026 MyIdeApp. All rights reserved.",
               "es": "© 2026 MyIdeApp. Todos los derechos reservados."},
    "made": {"fr": "Conçu en France", "en": "Made in France", "es": "Hecho en Francia"},
}


# Glyphe Instagram (contour officiel simplifié) : sans lui, la liste ressemblait à
# une simple liste d'apps (retour de Lucas, 2026-10-12).
IG_GLYPH = ('<svg class="ig-glyph" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" '
            'fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" '
            'stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/></svg>')


def instagram_links():
    return "".join(
        f'<a class="site-footer__ig" href="https://www.instagram.com/{a["instagram"]}/" rel="noopener" target="_blank" '
        f'aria-label="{e(a["name"])} — Instagram @{e(a["instagram"])}">'
        f'<span class="site-footer__ig-icon"><img src="/assets/{a["slug"]}/icon-192.png" alt="" width="28" height="28" loading="lazy">'
        f'<span class="site-footer__ig-badge">{IG_GLYPH}</span></span>'
        f'<span class="site-footer__ig-text"><strong>{e(a["name"])}</strong><small>@{e(a["instagram"])}</small></span></a>'
        for a in APPS if a.get("instagram"))


def footer_inner(lang):
    return f"""      <div class="site-footer__grid">
        <div class="site-footer__brand">
          {LOGO}
          <p>{e(T['tagline'][lang])}</p>
        </div>
        <div class="site-footer__col">
          <h4>{e(T['question'][lang])}</h4>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <a href="/contact.html">{e(T['form'][lang])}</a>
          <span class="site-footer__note">{e(T['reply'][lang])}</span>
        </div>
        <div class="site-footer__col site-footer__col--ig">
          <h4 class="site-footer__ig-title">{IG_GLYPH}{e(T['insta'][lang])}</h4>
          <div class="site-footer__igs">{instagram_links()}</div>
          <a class="site-footer__ig-all" href="{IG_PAGE[lang]}">{IG_GLYPH}{e(T['ig_all'][lang])} →</a>
        </div>
        <div class="site-footer__col">
          <h4>{e(T['res'][lang])}</h4>
          <a href="{APPS_PAGE[lang]}">{e(T['all_apps'][lang])}</a>
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


NAV_LABELS = {"apps": {"fr": "Ce qu'on fait", "en": "What We Do", "es": "Lo que hacemos"},
              "about": {"fr": "Qui sommes-nous", "en": "Who We Are", "es": "Quiénes somos"},
              "guides": {"fr": "Guides", "en": "Guides", "es": "Guías"},
              "instagram": {"fr": "Instagram", "en": "Instagram", "es": "Instagram"},
              "contact": {"fr": "Contact", "en": "Contact", "es": "Contacto"}}
NAV_KEYS = {"apps": "nav_apps", "guides": "nav_guides", "about": "nav_about", "instagram": "nav_instagram", "contact": "nav_contact"}
LANG_NAMES = {"fr": "Français", "en": "English", "es": "Español"}
GLOBE = ('<svg class="lang-menu__globe" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" '
         'stroke="currentColor" stroke-width="1.6"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9'
         's1.3-6.4 3.8-9z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>')
CHEVRON = ('<svg class="lang-menu__chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" '
           'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
LOGO = ('<a href="/" class="studio-logo" aria-label="MyIdeApp"><img src="/assets/favicon.svg" alt="" width="34" height="34">'
        '<span class="studio-logo__word">My<span class="tt-hl">IdeA</span>pp</span></a>')


def _nav(links, lang_label, lang_items):
    """Barre du studio, à la manière de wearebluefoxes.com : logo à gauche, menu et
    langue (globe + liste déroulante) groupés à droite, menu « burger » sur mobile.
    Liste déroulante et burger en <details> : ils marchent sans JavaScript (guides
    et À propos n'en chargent pas)."""
    return f"""  <nav class="navbar studio-nav">
    {LOGO}
    <div class="studio-nav__right">
      <div class="navbar__nav studio-nav__links">
{links}
      </div>
      <details class="lang-menu">
        <summary class="lang-menu__btn">{GLOBE}{lang_label}{CHEVRON}</summary>
        <div class="lang-menu__list">{lang_items}</div>
      </details>
      <details class="studio-nav__burger">
        <summary aria-label="Menu"><span></span><span></span><span></span></summary>
        <div class="studio-nav__panel">
{links}
        </div>
      </details>
    </div>
  </nav>"""


def nav(lang, lang_links, active=None, about_href=None):
    """Pages générées dans une langue fixe : libellés écrits, langues = liens vers l'autre URL."""
    hrefs = {"apps": APPS_PAGE[lang], "guides": "/guides/", "about": about_href or ABOUT[lang], "instagram": IG_PAGE[lang],
             "contact": "/contact.html"}
    active_cls = ' class="active"'
    links = "\n".join(f'        <a href="{hrefs[k]}"{active_cls if k == active else ""}>{e(NAV_LABELS[k][lang])}</a>'
                      for k in NAV_LABELS)
    items = "".join(f'<a class="lang-btn{" active" if l == lang else ""}" href="{u}" hreflang="{l}" lang="{l}">{LANG_NAMES[l]}</a>'
                    for l, u in lang_links.items())
    return _nav(links, f"<span>{LANG_NAMES[lang]}</span>", items)


def nav_multi(active=None):
    """Pages traduites par i18n.js : libellés par clés, langues = boutons."""
    hrefs = {"apps": "/apps/", "guides": "/guides/", "about": "/a-propos/", "instagram": "/instagram/", "contact": "/contact.html"}
    def link(k):
        extra = {"apps": ' data-i18n-href="nav_apps_href"', "about": ' data-i18n-href="nav_about_href"',
                 "instagram": ' data-i18n-href="nav_instagram_href"'}.get(k, "")
        cls = ' class="active"' if k == active else ""
        return f'        <a href="{hrefs[k]}" data-i18n="{NAV_KEYS[k]}"{extra}{cls}>{e(NAV_LABELS[k]["fr"])}</a>'
    links = "\n".join(link(k) for k in NAV_LABELS)
    items = "".join(f'<button type="button" class="lang-btn" data-lang-btn="{l}" lang="{l}">{LANG_NAMES[l]}</button>' for l in LANGS)
    return _nav(links, '<span data-i18n="lang_name">Français</span>', items)


# ─── Photos et valeurs du studio (accueil, À propos, Contact) ────────────────
# Photos Unsplash (licence Unsplash : usage commercial gratuit, sans obligation de
# crédit — on crédite quand même, sur la page À propos). Ce sont des illustrations :
# jamais présentées comme de vrais utilisateurs ni comme l'équipe.
PHOTOS = {
    "amis-cafe": {"credit": "Vitaly Gariev", "id": "QaFcC7GtoJs",
                  "alt": {"fr": "Quatre amis regardent un téléphone autour d'un café", "en": "Four friends looking at a phone over coffee",
                          "es": "Cuatro amigos miran un teléfono tomando un café"}},
    "mains-cafe": {"credit": "Vitaly Gariev", "id": "1s1zWWELg3c",
                   "alt": {"fr": "Des mains tiennent des téléphones autour de tasses de café", "en": "Hands holding phones around cups of coffee",
                           "es": "Manos con teléfonos alrededor de tazas de café"}},
    "selfie-amies": {"credit": "Sandisk", "id": "pAKgXLu04CQ",
                     "alt": {"fr": "Quatre amies prennent un selfie en riant", "en": "Four friends laughing while taking a selfie",
                             "es": "Cuatro amigas se hacen un selfi riendo"}},
    "amis-rire": {"credit": "Karthik Balakrishnan", "id": "Y4zNMW3pQAs",
                  "alt": {"fr": "Deux amis rient devant un téléphone", "en": "Two friends laughing at a phone",
                          "es": "Dos amigos se ríen mirando un teléfono"}},
    "amies-ville": {"credit": "Vitaly Gariev", "id": "Evszshc7XWg",
                    "alt": {"fr": "Deux amies rient en regardant un téléphone", "en": "Two friends laughing while looking at a phone",
                            "es": "Dos amigas se ríen mirando un teléfono"}},
    "amis-dehors": {"credit": "Hiki App", "id": "aM-BRQtrng8",
                    "alt": {"fr": "Deux amis rient dehors devant leur téléphone", "en": "Two friends laughing outdoors at their phone",
                            "es": "Dos amigos se ríen al aire libre con su teléfono"}},
}


def photo(name, lang, cls="photo", sizes="(max-width: 820px) 100vw, 50vw", eager=False):
    p = PHOTOS[name]
    load = "" if eager else ' loading="lazy"'
    return (f'<img class="{cls}" src="/assets/photos/{name}-1600.jpg" srcset="/assets/photos/{name}-800.jpg 800w, '
            f'/assets/photos/{name}-1600.jpg 1600w" sizes="{sizes}" alt="{e(p["alt"][lang])}"{load} decoding="async">')


def credits(lang):
    lead = {"fr": "Photos : ", "en": "Photos: ", "es": "Fotos: "}[lang]
    names = sorted({p["credit"] for p in PHOTOS.values()})
    return lead + ", ".join(names) + " (Unsplash)"


VALUES = {
    "fr": [("Mode incognito par défaut", "Pas de compte obligatoire : tu ouvres l'app et tu t'en sers, tout de suite."),
           ("Tes données chez toi", "Ton cycle, tes courses, tes dépenses, tes notes : sur ton iPhone, pas sur un serveur. Rien n'est revendu."),
           ("Une app, un usage", "Chaque app fait une seule chose, simplement, sans fonctions inutiles."),
           ("Clair et sans jugement", "Gratuit au téléchargement, Premium affiché en clair, et des apps pensées pour tout le monde, en 9 langues.")],
    "en": [("Incognito by default", "No account required: open the app and use it, right away."),
           ("Your data stays with you", "Your cycle, runs, spending, notes: on your iPhone, not on a server. Nothing is sold."),
           ("One app, one job", "Each app does one thing, simply, with no needless features."),
           ("Clear and judgment-free", "Free to download, Premium price shown upfront, and apps built for everyone, in 9 languages.")],
    "es": [("Modo incógnito por defecto", "Sin cuenta obligatoria: abres la app y la usas, al momento."),
           ("Tus datos contigo", "Tu ciclo, tus carreras, tus gastos, tus notas: en tu iPhone, no en un servidor. Nada se vende."),
           ("Una app, un uso", "Cada app hace una sola cosa, con sencillez, sin funciones inútiles."),
           ("Claro y sin juicios", "Descarga gratuita, Premium con precio claro y apps pensadas para todos, en 9 idiomas.")],
}
WHY_TITLE = {"fr": ("Pourquoi", "MyIdeApp ?"), "en": ("Why", "MyIdeApp?"), "es": ("¿Por qué", "MyIdeApp?")}


def values_list(lang):
    return "\n".join(f'          <div class="value"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in VALUES[lang])
