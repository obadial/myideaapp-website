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
    "intro": {"fr": "MyIdeApp conçoit des apps qui font une seule chose, et la font bien : suivre son cycle, courir sans réseau social, boire assez d'eau, tenir son budget… Toutes suivent la même règle : pas de compte obligatoire, et tes données personnelles restent sur ton téléphone. Elles sont gratuites au téléchargement, aujourd'hui sur iPhone.",
              "en": "MyIdeApp builds apps that do one thing and do it well: tracking your cycle, running without a social feed, drinking enough water, sticking to a budget… They all follow the same rule: no account required, and your personal data stays on your phone. They're free to download, available today on iPhone.",
              "es": "MyIdeApp crea apps que hacen una sola cosa, y la hacen bien: seguir tu ciclo, correr sin red social, beber suficiente agua, cuidar tu presupuesto… Todas siguen la misma regla: sin cuenta obligatoria, y tus datos personales se quedan en tu teléfono. Son gratis, hoy en iPhone."},
    "crumb": {"fr": "Ce qu'on fait", "en": "What We Do", "es": "Lo que hacemos"},
    "compare": {"fr": "Tu hésites avec une autre app ? Lis nos comparatifs", "en": "Weighing up another app? Read our comparisons",
                "es": "¿Dudas con otra app? Lee nuestras comparativas"},
}

# Les apps rangées par grands besoins (remplace les filtres : la page se lit sans cliquer).
GROUPS = [
    ("body", ["rhythm", "nova", "hydrome", "enjoymeal"],
     {"fr": ["Prendre soin", "de son corps"], "en": ["Take care", "of your body"], "es": ["Cuidar", "tu cuerpo"]},
     {"fr": "Comprendre son cycle, suivre sa santé intime, boire assez d'eau ou manger sans culpabiliser : des apps douces, sans jugement, où tes données de santé restent chez toi.",
      "en": "Understand your cycle, track your sexual health, drink enough water or eat without guilt: gentle, judgment-free apps where your health data stays with you.",
      "es": "Entender tu ciclo, seguir tu salud íntima, beber suficiente agua o comer sin culpa: apps amables, sin juicios, donde tus datos de salud se quedan contigo."}),
    ("move", ["runfree"],
     {"fr": ["Bouger", "à ton rythme"], "en": ["Move", "at your own pace"], "es": ["Moverte", "a tu ritmo"]},
     {"fr": "Courir pour soi, sans fil d'actualité ni classement : ton GPS, tes parcours et tes records restent sur ton téléphone.",
      "en": "Run for yourself, with no feed and no leaderboard: your GPS, routes and records stay on your phone.",
      "es": "Correr para ti, sin feed ni clasificaciones: tu GPS, tus rutas y tus récords se quedan en tu teléfono."}),
    ("mind", ["lunarest", "inhale", "mantrame"],
     {"fr": ["Dormir, respirer,", "se recentrer"], "en": ["Sleep, breathe,", "refocus"], "es": ["Dormir, respirar,", "centrarte"]},
     {"fr": "Des sons pour s'endormir, des exercices de respiration guidés, une affirmation par jour : des moments de calme, à ton rythme.",
      "en": "Sounds to fall asleep, guided breathing exercises, one affirmation a day: moments of calm, at your own pace.",
      "es": "Sonidos para dormir, ejercicios de respiración guiados, una afirmación al día: momentos de calma, a tu ritmo."}),
    ("money", ["budgetbrief", "stockwatch"],
     {"fr": ["Gérer", "son argent"], "en": ["Manage", "your money"], "es": ["Gestionar", "tu dinero"]},
     {"fr": "Noter ses dépenses sans connecter sa banque, ou s'entraîner à la Bourse avec un portefeuille virtuel, sans argent réel.",
      "en": "Log your spending without connecting your bank, or practice investing with a virtual portfolio and no real money.",
      "es": "Anotar tus gastos sin conectar tu banco, o practicar en bolsa con una cartera virtual, sin dinero real."}),
    ("life", ["myfoodbook", "chapter"],
     {"fr": ["Cuisine et", "vie perso"], "en": ["Cooking and", "personal life"], "es": ["Cocina y", "vida personal"]},
     {"fr": "Garder ses recettes au même endroit, même hors ligne, ou tenir un carnet de rencontres privé, protégé par Face ID.",
      "en": "Keep your recipes in one place, even offline, or keep a private dating journal protected by Face ID.",
      "es": "Guardar tus recetas en un solo lugar, incluso sin conexión, o llevar un diario de citas privado protegido con Face ID."}),
]

# Faits vérifiés le 2026-10-12 dans data/apps.json : Premium dès 0,99 €/mois (bientôt pour
# HydroMe et MyFoodBook), iOS 15 ou 16 selon l'app, 9 langues. Android : pas de date annoncée.
COMMON_TITLE = {"fr": ["Ce que nos apps", "ont en commun"], "en": ["What our apps", "have in common"], "es": ["Lo que nuestras apps", "tienen en común"]}
COMMON = {
    "fr": [("Gratuites au téléchargement", "Le Premium est optionnel, à partir de 0,99 €/mois, avec son prix affiché sur chaque page d'app."),
           ("Sans compte obligatoire", "Tu ouvres l'app et tu t'en sers, tout de suite."),
           ("Tes données sur ton téléphone", "Ton cycle, tes courses, tes dépenses ou tes notes ne sont pas stockés sur nos serveurs, et rien n'est revendu."),
           ("En 9 langues", "Français, anglais, espagnol, allemand, italien, portugais (Portugal et Brésil), hindi et arabe."),
           ("Aujourd'hui sur iPhone", "Compatibles iOS 15 ou 16 selon l'app. La version Android arrive bientôt sur Google Play.")],
    "en": [("Free to download", "Premium is optional, from €0.99/month, with its price shown on every app page."),
           ("No account required", "Open the app and use it, right away."),
           ("Your data on your phone", "Your cycle, runs, spending or notes aren't stored on our servers, and nothing is sold."),
           ("In 9 languages", "English, French, Spanish, German, Italian, Portuguese (Portugal and Brazil), Hindi and Arabic."),
           ("On iPhone today", "Compatible with iOS 15 or 16 depending on the app. The Android version is coming soon to Google Play.")],
    "es": [("Gratis", "El Premium es opcional, desde 0,99 €/mes, con su precio indicado en cada página de app."),
           ("Sin cuenta obligatoria", "Abres la app y la usas, al momento."),
           ("Tus datos en tu teléfono", "Tu ciclo, tus carreras, tus gastos o tus notas no se guardan en nuestros servidores, y nada se vende."),
           ("En 9 idiomas", "Español, inglés, francés, alemán, italiano, portugués (Portugal y Brasil), hindi y árabe."),
           ("Hoy en iPhone", "Compatibles con iOS 15 o 16 según la app. La versión Android llega pronto a Google Play.")],
}
FAQ_TITLE = {"fr": ["Questions", "fréquentes"], "en": ["Frequently asked", "questions"], "es": ["Preguntas", "frecuentes"]}
FAQ = {
    "fr": [("Les apps MyIdeApp sont-elles gratuites ?", "Oui, toutes sont gratuites au téléchargement. Certaines proposent un Premium optionnel, à partir de 0,99 €/mois, dont le prix est affiché sur la page de l'app."),
           ("Faut-il créer un compte ?", "Non. Aucune de nos apps n'oblige à créer un compte : tu peux t'en servir dès l'ouverture."),
           ("Où sont stockées mes données ?", "Sur ton téléphone. Tes données personnelles (cycle, courses, dépenses, notes…) ne sont pas envoyées sur nos serveurs et ne sont jamais revendues. Le détail est dans la politique de confidentialité de chaque app."),
           ("Les apps existent-elles sur Android ?", "Pas encore : elles sont aujourd'hui sur iPhone, et la version Android arrive bientôt sur Google Play.")],
    "en": [("Are MyIdeApp apps free?", "Yes, they're all free to download. Some offer an optional Premium, from €0.99/month, with its price shown on the app's page."),
           ("Do I need to create an account?", "No. None of our apps require an account: you can use them as soon as you open them."),
           ("Where is my data stored?", "On your phone. Your personal data (cycle, runs, spending, notes…) isn't sent to our servers and is never sold. Each app's privacy policy has the details."),
           ("Are the apps available on Android?", "Not yet: they're on iPhone today, and the Android version is coming soon to Google Play.")],
    "es": [("¿Las apps de MyIdeApp son gratis?", "Sí, todas se descargan gratis. Algunas ofrecen un Premium opcional, desde 0,99 €/mes, con su precio indicado en la página de la app."),
           ("¿Hay que crear una cuenta?", "No. Ninguna de nuestras apps obliga a crear una cuenta: puedes usarlas nada más abrirlas."),
           ("¿Dónde se guardan mis datos?", "En tu teléfono. Tus datos personales (ciclo, carreras, gastos, notas…) no se envían a nuestros servidores y nunca se venden. La política de privacidad de cada app tiene el detalle."),
           ("¿Las apps están en Android?", "Todavía no: hoy están en iPhone, y la versión Android llega pronto a Google Play.")],
}


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


def cards_by_slug(lang):
    html_src = catalog(lang)
    cards = {}
    for m in re.finditer(r'\s*<!-- [^>]+ -->\s*(<a [^>]*class="app-card app-card--([a-z]+)[^"]*".*?</a>)', html_src, re.S):
        cards[m.group(2)] = re.sub(r" fade-up(?:-delay-\d)?", "", m.group(1))
    missing = {sl for _, sls, _, _ in GROUPS for sl in sls} - set(cards)
    if missing:
        raise SystemExit(f"cartes introuvables dans data/apps_catalog.html : {missing}")
    return cards


def page(lang):
    alternates = {l: BASE + site_shell.APPS_PAGE[l] for l in LANGS}
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": TXT["title"][lang], "url": BASE + site_shell.APPS_PAGE[lang],
           "inLanguage": lang, "isPartOf": {"@id": BASE + "/#organization"},
           "mainEntity": {"@type": "ItemList", "numberOfItems": len(APPS), "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "name": a["name"], "url": BASE + L.url(a["slug"], lang)}
               for i, a in enumerate(APPS)]}}]
    cards = cards_by_slug(lang)
    groups = "\n".join(f"""      <section class="app-group apps-section apps-section--page" id="{key}">
        <h2>{two_tone(title[lang])}</h2>
        <p class="app-group__text">{e(text[lang])}</p>
        <div class="apps-carousel">
          {"".join(cards[sl] for sl in slugs)}
        </div>
      </section>""" for key, slugs, title, text in GROUPS)
    common = "\n".join(f'          <div class="why__item"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in COMMON[lang])
    faq = "\n".join(f'        <details class="faq-item"><summary>{e(q)}</summary><p>{e(r)}</p></details>' for q, r in FAQ[lang])
    ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in FAQ[lang]]})
    out = G.head(lang, TXT["title"][lang].replace(" | MyIdeApp", ""), TXT["desc"][lang], BASE + site_shell.APPS_PAGE[lang],
                 alternates, "studio", ld).replace('content="article"', 'content="website"', 1)
    body = f"""
  <main class="guide apps-page">
    <div class="container">
      <p class="guide__crumbs"><a href="/">MyIdeApp</a> › {e(TXT['crumb'][lang])}</p>
      <h1 class="guide__title">{two_tone(TXT['h1'][lang])}</h1>
      <p class="guide__intro">{e(TXT['intro'][lang])}</p>
{groups}

      <section class="apps-common">
        <h2>{two_tone(COMMON_TITLE[lang])}</h2>
        <div class="apps-common__grid">
{common}
        </div>
      </section>

      <section class="apps-faq">
        <h2>{two_tone(FAQ_TITLE[lang])}</h2>
{faq}
      </section>
      <p class="apps-page__compare"><a href="/guides/">{e(TXT['compare'][lang])} →</a></p>
    </div>
  </main>
"""
    return out + "\n" + G.nav(lang, alternates, active="apps") + body + G.footer(lang)


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
