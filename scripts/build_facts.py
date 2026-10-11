#!/usr/bin/env python3
"""Encadré « En bref » factuel sur chaque page d'app, depuis data/apps.json.

Les moteurs IA citent les sources qui répondent net : prix exact, ce qui est
gratuit, où vont les données. L'encadré existe en dur en FR, EN et ES
(`data-lang-block`) : un robot lit les trois, le visiteur ne voit que la langue
choisie (règle CSS sur `html[lang]`, posé par js/i18n.js).

Idempotent, entre `<!-- facts:start -->` et `<!-- facts:end -->`, inséré juste
après la section #overview. Met aussi à jour les `offers` du JSON-LD.
    python3 scripts/build_facts.py
"""
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = json.loads((SITE / "data" / "apps.json").read_text(encoding="utf-8"))
START, END = "<!-- facts:start -->", "<!-- facts:end -->"
LANGS = ("fr", "en", "es")

L = {
    "title": {"fr": "{name} en bref", "en": "{name} at a glance", "es": "{name} en resumen"},
    "price": {"fr": "Prix", "en": "Price", "es": "Precio"},
    "free_label": {"fr": "Gratuit", "en": "Free", "es": "Gratis"},
    "premium_line": {
        "fr": "Téléchargement gratuit. Premium optionnel : {m_eur} €/mois ou {a_eur} €/an (États-Unis : ${m_usd}/mois ou ${a_usd}/an).",
        "en": "Free to download. Optional Premium: ${m_usd}/month or ${a_usd}/year (France: €{m_eur_en}/month or €{a_eur_en}/year).",
        "es": "Descarga gratuita. Premium opcional: {m_eur} €/mes o {a_eur} €/año (Estados Unidos: {m_usd} $/mes o {a_usd} $/año).",
    },
    "premium_soon": {
        "fr": "Téléchargement gratuit, toutes les fonctions incluses. Une option Premium sans publicité arrive bientôt.",
        "en": "Free to download, every feature included. An ad-free Premium option is coming soon.",
        "es": "Descarga gratuita, todas las funciones incluidas. Pronto llegará una opción Premium sin anuncios.",
    },
    "included": {"fr": "Inclus gratuitement", "en": "Free features", "es": "Incluido gratis"},
    "premium": {"fr": "Premium ajoute", "en": "Premium adds", "es": "Premium añade"},
    "data": {"fr": "Données", "en": "Data", "es": "Datos"},
    "data_v": {
        "fr": "Stockées uniquement sur ton appareil. Aucun compte obligatoire, aucune revente de données.",
        "en": "Stored only on your device. No account required, data never sold.",
        "es": "Guardados solo en tu dispositivo. Sin cuenta obligatoria y sin venta de datos.",
    },
    "ads": {"fr": "Publicité", "en": "Ads", "es": "Publicidad"},
    "ads_v": {
        "fr": "Publicités plein écran occasionnelles dans la version gratuite, aucune en Premium.",
        "en": "Occasional full-screen ads in the free version, none with Premium.",
        "es": "Anuncios a pantalla completa ocasionales en la versión gratuita, ninguno con Premium.",
    },
    "langs": {"fr": "Langues", "en": "Languages", "es": "Idiomas"},
    "langs_v": {
        "fr": "9 : anglais, français, allemand, espagnol, italien, portugais (PT et BR), hindi, arabe",
        "en": "9: English, French, German, Spanish, Italian, Portuguese (PT and BR), Hindi, Arabic",
        "es": "9: inglés, francés, alemán, español, italiano, portugués (PT y BR), hindi, árabe",
    },
    "platforms": {"fr": "Plateformes", "en": "Platforms", "es": "Plataformas"},
    "platforms_v": {
        "fr": "iPhone (iOS {ios}+){health}. Android : bientôt.",
        "en": "iPhone (iOS {ios}+){health}. Android: coming soon.",
        "es": "iPhone (iOS {ios}+){health}. Android: próximamente.",
    },
    "health": {"fr": ", compatible Apple Santé", "en": ", works with Apple Health", "es": ", compatible con Apple Salud"},
    "updated": {"fr": "Informations vérifiées le {d}.", "en": "Information checked on {d}.", "es": "Información verificada el {d}."},
}


MONTHS = {
    "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(),
    "en": "January February March April May June July August September October November December".split(),
    "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(),
}


def human_date(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    month = MONTHS[lang][m - 1]
    return {"fr": f"{d} {month} {y}", "en": f"{month} {d}, {y}", "es": f"{d} de {month} de {y}"}[lang]


def t(key, lang, **kw):
    return L[key][lang].format(**kw)


def box(app, lang):
    p = app["price"]
    price = (t("premium_line", lang, m_eur=p["monthly_eur"], a_eur=p["annual_eur"], m_usd=p["monthly_usd"], a_usd=p["annual_usd"],
               m_eur_en=p["monthly_eur"].replace(",", "."), a_eur_en=p["annual_eur"].replace(",", "."))
             if app.get("premium_available", True) else t("premium_soon", lang))
    rows = [
        ("price", price),
        ("included", app["free"][lang]),
    ]
    if app.get("premium_available", True):
        rows.append(("premium", app["premium"][lang]))
    rows += [
        ("data", t("data_v", lang)),
        ("ads", t("ads_v", lang)),
        ("langs", t("langs_v", lang)),
        ("platforms", t("platforms_v", lang, ios=app["ios_min"], health=L["health"][lang] if app["apple_health"] else "")),
    ]
    dl = "\n".join(f"          <dt>{html.escape(L[k][lang])}</dt><dd>{html.escape(v)}</dd>" for k, v in rows)
    extra = f'\n        <p class="facts__note">{html.escape(app["extra"][lang])}</p>' if app.get("extra") else ""
    return f"""      <div class="facts" data-lang-block="{lang}" lang="{lang}">
        <h2 class="facts__title">{html.escape(t('title', lang, name=app['name']))}</h2>
        <dl class="facts__list">
{dl}
        </dl>{extra}
        <p class="facts__date">{html.escape(t('updated', lang, d=human_date(DATA['_meta']['updated'], lang)))}</p>
      </div>"""


def offers(app):
    base = [{"@type": "Offer", "price": "0", "priceCurrency": "EUR"}]
    if not app.get("premium_available", True):
        return base
    p = app["price"]
    for cur, m, a in (("EUR", p["monthly_eur"], p["annual_eur"]), ("USD", p["monthly_usd"], p["annual_usd"])):
        for name, val, unit in (("Premium monthly", m, "MON"), ("Premium annual", a, "ANN")):
            base.append({
                "@type": "Offer", "name": name, "price": val.replace(",", "."), "priceCurrency": cur,
                "priceSpecification": {"@type": "UnitPriceSpecification", "price": val.replace(",", "."),
                                       "priceCurrency": cur, "unitCode": unit},
            })
    return base


def main():
    for app in DATA["apps"]:
        path = SITE / app["slug"] / "index.html"
        page = path.read_text(encoding="utf-8")
        block = (f'{START}\n  <section class="section facts-section" id="en-bref">\n    <div class="container">\n'
                 + "\n".join(box(app, lg) for lg in LANGS)
                 + f"\n    </div>\n  </section>\n  {END}")
        if START in page:
            page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, page, flags=re.S)
        else:
            # Le hero est #overview sur 10 pages, `<section class="hero">` sur HydroMe et MantraMe.
            m = (re.search(r'<section id="overview".*?</section>', page, flags=re.S)
                 or re.search(r'<section class="hero">.*?</section>', page, flags=re.S))
            if not m:
                raise SystemExit(f"{app['slug']}: section hero introuvable")
            page = page[:m.end()] + "\n\n  " + block + page[m.end():]

        def fix(mm):
            data = json.loads(mm.group(1))
            if data.get("@type") != "SoftwareApplication":
                return mm.group(0)
            data["offers"] = offers(app)
            data["applicationCategory"] = data.get("applicationCategory", "LifestyleApplication")
            return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n  </script>"
        page = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix, page, flags=re.S)
        path.write_text(page, encoding="utf-8")
        print(f"ok {app['slug']}")


if __name__ == "__main__":
    main()
