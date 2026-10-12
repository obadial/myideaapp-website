#!/usr/bin/env python3
"""Page « À propos » du studio, en vraies pages FR / EN / ES.

Pourquoi (2026-10-12) : Google et les IA recommandent plus volontiers une
marque qu'ils savent identifier. Le site ne disait nulle part qui publie les
12 apps, ni ce qui sort réellement du téléphone. La page met le studio en
avant ; Lucas Obadia n'apparaît que comme fondateur, sans autre information
personnelle (choix explicite du 2026-10-12 : ni adresse, ni téléphone, ni âge).

    /a-propos/   /en/about/   /es/acerca-de/

Produit aussi assets/logo-512.png (logo carré lisible par Google, qui ignore
les logos SVG) et tient à jour le bloc `<!-- about -->` du sitemap.
Mise en page partagée avec les guides (head, nav, footer de build_guides).
    python3 scripts/build_about.py
"""
import datetime
import html
import json
import re
import subprocess
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_guides as G  # noqa: E402
import site_shell  # noqa: E402

SITE = G.SITE
BASE = G.BASE
LANGS = G.LANGS
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
PATHS = {"fr": "/a-propos/", "en": "/en/about/", "es": "/es/acerca-de/"}
DEV_PAGE = "https://apps.apple.com/developer/lucas-obadia/id1447668792"
UPDATED = "2026-10-12"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
e = html.escape

TXT = {
    "title": {"fr": "À propos de MyIdeApp, studio d'apps iPhone",
              "en": "About MyIdeApp, an independent iPhone app studio",
              "es": "Sobre MyIdeApp, estudio independiente de apps"},
    "desc": {"fr": "MyIdeApp est un studio indépendant français qui publie 12 apps iPhone simples : données sur ton téléphone, sans compte obligatoire, prix affichés.",
             "en": "MyIdeApp is an independent French studio publishing 12 simple iPhone apps: data on your phone, no account required, prices shown upfront.",
             "es": "MyIdeApp es un estudio independiente francés que publica 12 apps sencillas para iPhone: datos en tu teléfono, sin cuenta obligatoria, precios claros."},
    "h1": {"fr": ["MyIdeApp,", "un studio indépendant d'apps iPhone"], "en": ["MyIdeApp,", "an independent iPhone app studio"], "es": ["MyIdeApp,", "un estudio independiente de apps para iPhone"]},
    "intro": {"fr": "MyIdeApp conçoit et publie 12 apps iPhone : cycle menstruel, course à pied, hydratation, budget, Bourse, recettes, alimentation, sommeil, respiration, affirmations, santé intime et carnet de rencontres. Une app, un usage, fait simplement.",
              "en": "MyIdeApp designs and publishes 12 iPhone apps: period tracking, running, hydration, budgeting, stock market practice, recipes, food journaling, sleep, breathing, affirmations, sexual health and a dating journal. One app, one job, done simply.",
              "es": "MyIdeApp diseña y publica 12 apps para iPhone: ciclo menstrual, running, hidratación, presupuesto, bolsa, recetas, alimentación, sueño, respiración, afirmaciones, salud íntima y diario de citas. Una app, un uso, hecho con sencillez."},
    # Histoire racontée par Lucas le 2026-10-12 : studio créé début mai 2026, par lassitude des apps qui
    # demandent trop de données ; idée : les infos sur le téléphone, pas de compte, esprit « mode incognito ».
    "story_h": {"fr": ["Notre", "histoire"], "en": ["Our", "story"], "es": ["Nuestra", "historia"]},
    "story": {
        "fr": ["MyIdeApp est né début mai 2026 d'un ras-le-bol. Pour noter son cycle, boire assez d'eau ou suivre ses dépenses, la plupart des apps demandaient de créer un compte et de confier beaucoup trop de données, pour pas grand-chose en retour.",
               "Lucas Obadia, développeur indépendant, a voulu changer d'approche : rendre à chacun ses informations, directement sur son téléphone, et pouvoir se servir d'une app sans créer de compte. Un peu comme en navigation privée : tu ouvres, tu utilises, et tes informations restent sur ton téléphone.",
               "C'est devenu la règle du studio. Aujourd'hui, ce sont 12 apps en 9 langues, de la santé intime à la Bourse, avec la même promesse : simples, utiles, et tes données chez toi."],
        "en": ["MyIdeApp was born in early May 2026 out of frustration. To track a cycle, drink enough water or follow spending, most apps asked you to create an account and hand over far too much data, for very little in return.",
               "Lucas Obadia, an independent developer, wanted a different approach: give people their information back, right on their phone, and let them use an app without creating an account. A bit like private browsing: you open it, you use it, and your information stays on your phone.",
               "That became the studio's rule. Today it's 12 apps in 9 languages, from sexual health to the stock market, with the same promise: simple, useful, and your data stays with you."],
        "es": ["MyIdeApp nació a principios de mayo de 2026 de un hartazgo. Para registrar el ciclo, beber suficiente agua o seguir los gastos, la mayoría de las apps pedían crear una cuenta y ceder demasiados datos, a cambio de muy poco.",
               "Lucas Obadia, desarrollador independiente, quiso cambiar el enfoque: devolver a cada uno su información, directamente en su teléfono, y poder usar una app sin crear una cuenta. Un poco como la navegación privada: abres, usas, y tu información se queda en tu teléfono.",
               "Se convirtió en la regla del estudio. Hoy son 12 apps en 9 idiomas, de la salud íntima a la bolsa, con la misma promesa: sencillas, útiles y con tus datos contigo."]},
    "everyone_h": {"fr": ["Pensées pour", "tout le monde"], "en": ["Built for", "everyone"], "es": ["Pensadas para", "todos"]},
    "everyone": {"fr": "Quels que soient ton âge, ton corps, ta langue ou ta façon de vivre : nos apps sont pensées sans stéréotype ni culpabilisation.",
                 "en": "Whatever your age, body, language or way of life: our apps are designed with no stereotypes and no guilt.",
                 "es": "Sea cual sea tu edad, tu cuerpo, tu idioma o tu forma de vivir: nuestras apps están pensadas sin estereotipos ni culpa."},
    "out_h": {"fr": ["Ce qui sort", "de ton téléphone"], "en": ["What leaves", "your phone"], "es": ["Qué sale", "de tu teléfono"]},
    "out_intro": {"fr": "Pour être transparents, voici les seuls services extérieurs utilisés, selon l'app :",
                  "en": "To be transparent, these are the only outside services used, depending on the app:",
                  "es": "Para ser transparentes, estos son los únicos servicios externos que se usan, según la app:"},
    "out": {
        "fr": ["Publicités dans les versions gratuites (Google AdMob), selon ton consentement.",
               "Abonnements Premium gérés par Apple, avec RevenueCat pour vérifier l'abonnement.",
               "Statistiques d'usage anonymes (Firebase, Google) dans certaines apps.",
               "EnjoyMeal : si tu configures ta propre clé, la photo d'un repas est envoyée au service d'IA que tu as choisi pour le reconnaître.",
               "StockWatch : les cours de Bourse viennent d'un fournisseur de données de marché."],
        "en": ["Ads in the free versions (Google AdMob), based on your consent.",
               "Premium subscriptions handled by Apple, with RevenueCat to verify the subscription.",
               "Anonymous usage statistics (Firebase, Google) in some apps.",
               "EnjoyMeal: if you set up your own key, a meal photo is sent to the AI service you chose to recognize it.",
               "StockWatch: stock prices come from a market data provider."],
        "es": ["Publicidad en las versiones gratuitas (Google AdMob), según tu consentimiento.",
               "Suscripciones Premium gestionadas por Apple, con RevenueCat para verificar la suscripción.",
               "Estadísticas de uso anónimas (Firebase, Google) en algunas apps.",
               "EnjoyMeal: si configuras tu propia clave, la foto de una comida se envía al servicio de IA que elegiste para reconocerla.",
               "StockWatch: las cotizaciones vienen de un proveedor de datos de mercado."],
    },
    "out_more": {"fr": "Le détail exact figure dans la politique de confidentialité de chaque app.",
                 "en": "The exact details are in each app's privacy policy.",
                 "es": "El detalle exacto está en la política de privacidad de cada app."},
    "apps_h": {"fr": ["Les 12", "apps"], "en": ["The 12", "apps"], "es": ["Las 12", "apps"]},
    "contact_h": {"fr": ["Nous", "contacter"], "en": ["Contact", "us"], "es": ["Escríbenos", ""]},
    "contact": {"fr": "Une question, un bug, une suggestion ? Écris-nous, on répond sous 48 h.",
                "en": "A question, a bug, a suggestion? Write to us, we reply within 48 hours.",
                "es": "¿Una pregunta, un error, una sugerencia? Escríbenos, respondemos en 48 h."},
    "form": {"fr": "Formulaire de contact", "en": "Contact form", "es": "Formulario de contacto"},
    "store": {"fr": "Toutes nos apps sur l'App Store", "en": "All our apps on the App Store", "es": "Todas nuestras apps en la App Store"},
    "legal": {"fr": "Informations légales : voir les mentions légales.", "en": "Legal information: see the legal notice.",
              "es": "Información legal: ver el aviso legal."},
    "updated": {"fr": "Mis à jour le 12 octobre 2026", "en": "Updated October 12, 2026", "es": "Actualizado el 12 de octubre de 2026"},
    "about": {"fr": "À propos", "en": "About", "es": "Acerca de"},
}


def two_tone(parts):
    hl, rest = parts
    return f'<span class="tt-hl">{e(hl)}</span> {e(rest)}'.rstrip()


def i18n():
    src = (SITE / "js/i18n.js").read_text(encoding="utf-8")
    return json.loads(subprocess.check_output(
        ["node", "-e", src + "\nprocess.stdout.write(JSON.stringify(TRANSLATIONS));"], text=True))


def app_path(slug, lang):
    return f"/{slug}/" if lang == "fr" else f"/{lang}/{slug}/"


def organization():
    return {"@type": "Organization", "@id": BASE + "/#organization", "name": "MyIdeApp", "url": BASE + "/",
            "logo": BASE + "/assets/logo-512.png", "email": "contact.myideapp@icloud.com",
            "description": TXT["desc"]["en"], "foundingDate": "2026-05", "foundingLocation": {"@type": "Country", "name": "France"},
            "founder": {"@type": "Person", "name": "Lucas Obadia", "jobTitle": "Independent iOS developer"},
            "sameAs": [DEV_PAGE]}


def page(lang, T):
    alternates = {l: BASE + PATHS[l] for l in LANGS}
    ld = [{"@context": "https://schema.org", "@type": "AboutPage", "url": BASE + PATHS[lang], "name": TXT["title"][lang],
           "inLanguage": lang, "dateModified": UPDATED, "mainEntity": organization()}]
    out = G.head(lang, TXT["title"][lang], TXT["desc"][lang], BASE + PATHS[lang], alternates, "studio", ld)
    out = out.replace('content="article"', 'content="website"', 1)
    story = "\n".join(f"          <p>{e(x)}</p>" for x in TXT["story"][lang])
    outside = "\n".join(f"          <li>{e(x)}</li>" for x in TXT["out"][lang])
    apps = "\n".join(
        f'          <a class="about-app" href="{app_path(a["slug"], lang)}"><img src="/assets/{a["slug"]}/icon-192.png" alt="" width="48" height="48" loading="lazy">'
        f'<span><strong>{e(a["name"])}</strong><small>{e(T[lang][a["slug"] + "_subtitle"])}</small></span></a>' for a in APPS)
    body = f"""
  <main class="guide about">
    <div class="container guide__inner">
      <p class="guide__crumbs"><a href="/">MyIdeApp</a> › {e(TXT['about'][lang])}</p>
      <h1 class="guide__title">{two_tone(TXT['h1'][lang])}</h1>
      <p class="guide__intro">{e(TXT['intro'][lang])}</p>

      <section class="split">
        <div class="split__text">
          <h2>{two_tone(TXT['story_h'][lang])}</h2>
{story}
        </div>
        <div class="split__media">{site_shell.photo("amies-ville", lang)}</div>
      </section>

      <section class="split split--reverse">
        <div class="split__media">{site_shell.photo("amis-dehors", lang)}</div>
        <div class="split__text">
          <h2>{two_tone(site_shell.WHY_TITLE[lang])}</h2>
          <div class="values">
{site_shell.values_list(lang)}
          </div>
        </div>
      </section>

      <section class="everyone">
        <h2>{two_tone(TXT['everyone_h'][lang])}</h2>
        <p>{e(TXT['everyone'][lang])}</p>
        <div class="everyone__photos">{site_shell.photo("selfie-amies", lang, sizes="(max-width: 820px) 100vw, 50vw")}{site_shell.photo("amis-rire", lang, sizes="(max-width: 820px) 100vw, 50vw")}</div>
      </section>

      <section>
        <h2>{two_tone(TXT['out_h'][lang])}</h2>
        <p>{e(TXT['out_intro'][lang])}</p>
        <ul>
{outside}
        </ul>
        <p>{e(TXT['out_more'][lang])}</p>
      </section>

      <section>
        <h2>{two_tone(TXT['apps_h'][lang])}</h2>
        <div class="about-apps">
{apps}
        </div>
        <p><a href="{DEV_PAGE}" rel="noopener" target="_blank">{e(TXT['store'][lang])} →</a></p>
      </section>

      <section>
        <h2>{two_tone(TXT['contact_h'][lang])}</h2>
        <p>{e(TXT['contact'][lang])}</p>
        <p><a href="mailto:contact.myideapp@icloud.com">contact.myideapp@icloud.com</a> · <a href="/contact.html">{e(TXT['form'][lang])}</a></p>
        <p class="guide__checked"><a href="/mentions-legales.html">{e(TXT['legal'][lang])}</a> · {e(TXT['updated'][lang])}</p>
        <p class="guide__checked">{e(site_shell.credits(lang))}</p>
      </section>
    </div>
  </main>
"""
    nav = G.nav(lang, alternates, active="about")
    return out + "\n" + nav + body + G.footer(lang)


def logo():
    out = SITE / "assets/logo-512.png"
    svg = (SITE / "assets/favicon.svg").read_text(encoding="utf-8")
    doc = (f'<!doctype html><html><head><link rel="stylesheet" href="{(SITE / "css/fonts.css").as_uri()}">'
           '<style>html,body{margin:0;width:512px;height:512px;overflow:hidden;background:transparent}'
           f'svg{{width:512px;height:512px;display:block}}</style></head><body>{svg}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "logo.html"
        f.write_text(doc, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                        "--allow-file-access-from-files", "--virtual-time-budget=2000", "--window-size=512,512",
                        f"--screenshot={out}", f.as_uri()], check=True, capture_output=True)


def sitemap():
    p = SITE / "sitemap.xml"
    sm = p.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    entries = "\n".join(f"  <url>\n    <loc>{BASE}{PATHS[l]}</loc>\n    <lastmod>{today}</lastmod>\n"
                        f"    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>" for l in LANGS)
    block = f"  <!-- about:start -->\n{entries}\n  <!-- about:end -->"
    if "<!-- about:start -->" in sm:
        sm = re.sub(r"  <!-- about:start -->.*?<!-- about:end -->", lambda _: block, sm, flags=re.S)
    else:
        sm = sm.replace("</urlset>", block + "\n\n</urlset>")
    p.write_text(sm, encoding="utf-8")


def main():
    T = i18n()
    for lang in LANGS:
        out = SITE / PATHS[lang].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang, T), encoding="utf-8")
    if not (SITE / "assets/logo-512.png").exists():
        logo()
    sitemap()
    print("À propos : 3 pages, logo 512 px, sitemap à jour")


if __name__ == "__main__":
    main()
