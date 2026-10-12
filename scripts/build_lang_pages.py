#!/usr/bin/env python3
"""Pages d'app en anglais et en espagnol, chacune à sa propre URL.

Pourquoi (2026-10-12) : les 12 pages d'app servaient les trois langues sur une
seule URL, la langue étant choisie en JavaScript d'après le navigateur. Google
le déconseille explicitement (« utilisez des URL différentes pour chaque
langue ») : Googlebot crawle en anglais et voyait la page traduite, Bing et les
robots d'IA voyaient le français, et l'espagnol n'était jamais indexé.

La page française `<app>/index.html` reste la source unique et garde son URL
(liée depuis l'App Store, AdMob et Google Play). Ce script :

1. complète la page française : liens hreflang, image de partage de l'app,
   boutons de langue transformés en liens, langue fixée (`data-lang-static`) ;
2. génère `/en/<app>/` et `/es/<app>/` : textes traduits directement dans le
   HTML depuis js/i18n.js (mêmes règles que I18n.apply), blocs `data-lang-block`
   des autres langues retirés, titre, canonical, données structurées (FAQ de
   data/faq.json, prix en dollars pour l'anglais) et liens vers les autres apps
   et le guide dans la même langue ;
3. tient à jour le bloc `<!-- lang-pages -->` du sitemap.

Une clé de traduction manquante fait échouer le script : une page anglaise ne
doit jamais contenir de français. Idempotent ; à relancer après toute
modification d'une page d'app ou de js/i18n.js (et après les autres scripts
qui modifient les pages françaises).
    python3 scripts/build_lang_pages.py
"""
import datetime
import html
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
BASE = "https://myideapp.com"
LANGS = ("fr", "en", "es")
OG_LOCALE = {"fr": "fr_FR", "en": "en_US", "es": "es_ES"}
SHOT = {"fr": "fr-FR", "en": "en-US", "es": "es-ES"}
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
SLUGS = [a["slug"] for a in APPS]
GUIDES = json.loads((SITE / "data/guides.json").read_text(encoding="utf-8"))["guides"]
FAQ = json.loads((SITE / "data/faq.json").read_text(encoding="utf-8"))
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
TODAY = datetime.date.today().isoformat()


def translations():
    src = (SITE / "js/i18n.js").read_text(encoding="utf-8")
    return json.loads(subprocess.check_output(
        ["node", "-e", src + "\nprocess.stdout.write(JSON.stringify(TRANSLATIONS));"], text=True))


T = translations()


def url(slug, lang):
    return f"/{slug}/" if lang == "fr" else f"/{lang}/{slug}/"


# ─── Repérage des éléments dans le HTML source, sans le reformater ───────────

class Elements(HTMLParser):
    """Liste les éléments avec leurs positions : début, début du contenu, fin."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer("\n", src):
            self.lines.append(m.end())
        self.stack, self.found = [], []
        self.feed(src)
        self.close()

    def _pos(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self._pos()
        text = self.get_starttag_text()
        el = {"tag": tag, "attrs": dict(attrs), "start": start, "open_end": start + len(text)}
        if tag in VOID or text.endswith("/>"):
            el["inner"], el["end"] = None, el["open_end"]
            self.found.append(el)
        else:
            self.stack.append(el)

    def handle_endtag(self, tag):
        pos = self._pos()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                el = self.stack.pop(i)
                del self.stack[i:]
                el["inner"] = (el["open_end"], pos)
                el["end"] = self.src.index(">", pos) + 1
                self.found.append(el)
                return


def edit(src, changes):
    """Applique des remplacements (début, fin, texte) qui ne se chevauchent pas."""
    for start, end, text in sorted(changes, key=lambda c: c[0], reverse=True):
        src = src[:start] + text + src[end:]
    return src


def set_attr(tag_text, name, value):
    """Remplace ou ajoute un attribut dans une balise ouvrante (sans toucher data-…-name)."""
    value = html.escape(value, quote=True)
    pat = re.compile(r'(?<=[\s])' + re.escape(name) + r'="[^"]*"')
    if pat.search(tag_text):
        return pat.sub(lambda _: f'{name}="{value}"', tag_text, count=1)
    return re.sub(r"\s*/?>$", lambda m: f' {name}="{value}"' + m.group(0).lstrip(), tag_text, count=1)


def tr(key, lang, el, slug):
    raw = T[lang].get(key)
    if raw is None:
        raise SystemExit(f"{slug} [{lang}] : clé de traduction absente « {key} »")
    app = el["attrs"].get("data-i18n-app")
    return re.sub(r"\{(\w+)\}", lambda m: app if m.group(1) == "app" and app else m.group(0), raw)


# ─── Transformations ─────────────────────────────────────────────────────────

def lang_links(src, slug, current):
    """Boutons de langue → liens vers les trois URL, état actif fixé dans le HTML."""
    def rep(m):
        code = m.group(1)
        cls = "lang-btn active" if code == current else "lang-btn"
        return (f'<a class="{cls}" data-lang-btn="{code}" href="{url(slug, code)}" hreflang="{code}"'
                f' lang="{code}">{code.upper()}</a>')
    return re.sub(r'<(?:button|a) class="lang-btn[^"]*" data-lang-btn="(fr|en|es)"[^>]*>[A-Z]{2}</(?:button|a)>', rep, src)


def head_block(slug, lang):
    alts = "\n".join(f'  <link rel="alternate" hreflang="{l}" href="{BASE}{url(slug, l)}">' for l in LANGS)
    others = "\n".join(f'  <meta property="og:locale:alternate" content="{OG_LOCALE[l]}">' for l in LANGS if l != lang)
    return (f"<!-- lang:head:start -->\n{alts}\n"
            f'  <link rel="alternate" hreflang="x-default" href="{BASE}{url(slug, "en")}">\n'
            f'  <meta property="og:locale" content="{OG_LOCALE[lang]}">\n{others}\n'
            f'  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">\n'
            f'  <meta name="twitter:card" content="summary_large_image">\n  <!-- lang:head:end -->')


def common(src, slug, lang):
    """Ce qui vaut pour les trois langues, page française comprise."""
    src = re.sub(r'<html lang="[a-z]{2}"( data-lang-static)?', f'<html lang="{lang}" data-lang-static', src, count=1)
    src = lang_links(src, slug, lang)
    src = re.sub(r'(<meta property="og:image" content=")[^"]*"', lambda m: m.group(1) + f'{BASE}/assets/og/{slug}-{lang}.jpg"', src, count=1)
    block = head_block(slug, lang)
    if "<!-- lang:head:start -->" in src:
        src = re.sub(r"<!-- lang:head:start -->.*?<!-- lang:head:end -->", lambda _: block, src, flags=re.S)
    else:
        src = re.sub(r'(\n(\s*)<link rel="canonical"[^>]*>)', lambda m: m.group(1) + "\n" + m.group(2) + block, src, count=1)
    return src


def drop_other_blocks(src, lang):
    els = Elements(src).found
    gone = [e for e in els if e["attrs"].get("data-lang-block") not in (None, lang)]
    outer = [e for e in gone if not any(o is not e and o["start"] <= e["start"] and e["end"] <= o["end"] for o in gone)]
    changes = []
    for e in outer:
        start = src.rfind("\n", 0, e["start"]) + 1
        start = start if not src[start:e["start"]].strip() else e["start"]
        end = e["end"] + 1 if src[e["end"]:e["end"] + 1] == "\n" else e["end"]
        changes.append((start, end, ""))
    return edit(src, changes)


def translate(src, slug, lang):
    changes = []
    for e in Elements(src).found:
        a = e["attrs"]
        tag_text = src[e["start"]:e["open_end"]]
        new_tag = tag_text
        if "data-i18n-content" in a:
            new_tag = set_attr(new_tag, "content", tr(a["data-i18n-content"], lang, e, slug))
        if "data-i18n-href" in a:
            new_tag = set_attr(new_tag, "href", tr(a["data-i18n-href"], lang, e, slug))
        if "data-i18n-placeholder" in a:
            new_tag = set_attr(new_tag, "placeholder", tr(a["data-i18n-placeholder"], lang, e, slug))
        if "data-i18n-shot" in a and "src" in a:
            new_tag = set_attr(new_tag, "src", re.sub(r"screenshots/[A-Za-z-]+/", f"screenshots/{SHOT[lang]}/", a["src"]))
        if new_tag != tag_text:
            changes.append((e["start"], e["open_end"], new_tag))
        if "data-i18n" in a and e["inner"]:
            changes.append((e["inner"][0], e["inner"][1], html.escape(tr(a["data-i18n"], lang, e, slug), quote=False)))
    return edit(src, changes)


def guide_url(path, lang):
    for g in GUIDES:
        if path == f"/guides/fr/{g['slug']['fr']}/":
            return f"/guides/{lang}/{g['slug'][lang]}/"
    return path


def relink(src, slug, lang):
    """Liens relatifs → chemins depuis la racine, vers la même langue quand elle existe."""
    def fix(m):
        attr, val = m.group(1), m.group(2)
        if re.match(r"^(#|[a-z]+:|//|/)", val) and not val.startswith("/guides/fr/"):
            if val.startswith("https://apps.apple.com/fr/app/"):
                return f'{attr}="https://apps.apple.com/app/{val[len("https://apps.apple.com/fr/app/"):]}"'
            return m.group(0)
        if val.startswith("/"):
            path = val
        else:
            parts = [p for p in f"/{slug}/{val}".split("/")]
            out = []
            for p in parts[1:]:
                if p == "..":
                    out.pop() if out else None
                elif p not in (".", ""):
                    out.append(p)
            path = "/" + "/".join(out) + ("/" if val.endswith("/") or val in ("./", ".") else "")
        app = re.fullmatch(r"/([a-z]+)/(?:index\.html)?", path)
        if app and app.group(1) in SLUGS:
            path = url(app.group(1), lang)
        path = guide_url(path, lang)
        return f'{attr}="{path}"'
    return re.sub(r'\b(href|src)="([^"]*)"', fix, src)


def offers_usd(app):
    pr = app["price"]
    offers = [{"@type": "Offer", "price": "0", "priceCurrency": "USD"}]
    if app.get("premium_available", True):
        for name, key, unit in (("Premium monthly", "monthly_usd", "MON"), ("Premium annual", "annual_usd", "ANN")):
            offers.append({"@type": "Offer", "name": name, "price": pr[key], "priceCurrency": "USD",
                           "priceSpecification": {"@type": "UnitPriceSpecification", "price": pr[key],
                                                  "priceCurrency": "USD", "unitCode": unit}})
    return offers


def jsonld(src, app, lang):
    slug = app["slug"]

    def fix(m):
        data = json.loads(m.group(2))
        t = data.get("@type")
        if t == "SoftwareApplication":
            data["description"] = T[lang]["meta_" + slug + "_desc"]
            data["url"] = BASE + url(slug, lang)
            for k in ("downloadUrl",):
                if k in data:
                    data[k] = data[k].replace("apps.apple.com/fr/app/", "apps.apple.com/app/")
            if "sameAs" in data:
                data["sameAs"] = [s.replace("apps.apple.com/fr/app/", "apps.apple.com/app/") for s in data["sameAs"]]
            if lang == "en" and "price" in app:
                data["offers"] = offers_usd(app)
        elif t == "FAQPage":
            data["mainEntity"] = [{"@type": "Question", "name": i["q"][lang],
                                   "acceptedAnswer": {"@type": "Answer", "text": i["a"][lang]}}
                                  for i in FAQ["apps"][slug]]
        elif t == "BreadcrumbList":
            data["itemListElement"][-1]["item"] = BASE + url(slug, lang)
        return (f'<script type="application/ld+json"{m.group(1)}>\n'
                + json.dumps(data, ensure_ascii=False, indent=2) + "\n  </script>")
    return re.sub(r'<script type="application/ld\+json"([^>]*)>(.*?)</script>', fix, src, flags=re.S)


def head(src, app, lang):
    slug = app["slug"]
    title = f"{app['name']} — {T[lang][slug + '_subtitle']} | MyIdeApp"
    if len(title) > 60:
        title = title[:-len(" | MyIdeApp")]
    src = re.sub(r"<title>[^<]*</title>", lambda _: f"<title>{html.escape(title, quote=False)}</title>", src, count=1)
    src = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + html.escape(title) + '"', src, count=1)
    for pat in (r'(<link rel="canonical" href=")[^"]*"', r'(<meta property="og:url" content=")[^"]*"'):
        src = re.sub(pat, lambda m: m.group(1) + BASE + url(slug, lang) + '"', src, count=1)
    return src


def sitemap():
    p = SITE / "sitemap.xml"
    sm = p.read_text(encoding="utf-8")
    entries = "\n".join(
        f"  <url>\n    <loc>{BASE}{url(s, l)}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>"
        for l in ("en", "es") for s in SLUGS)
    block = f"  <!-- lang-pages:start -->\n{entries}\n  <!-- lang-pages:end -->"
    if "<!-- lang-pages:start -->" in sm:
        sm = re.sub(r"  <!-- lang-pages:start -->.*?<!-- lang-pages:end -->", lambda _: block, sm, flags=re.S)
    else:
        sm = sm.replace("</urlset>", block + "\n\n</urlset>")
    p.write_text(sm, encoding="utf-8")


def main():
    for app in APPS:
        slug = app["slug"]
        fr_path = SITE / slug / "index.html"
        fr = common(fr_path.read_text(encoding="utf-8"), slug, "fr")
        fr_path.write_text(fr, encoding="utf-8")
        for lang in ("en", "es"):
            page = common(fr, slug, lang)
            page = drop_other_blocks(page, lang)
            page = translate(page, slug, lang)
            page = jsonld(page, app, lang)
            page = head(page, app, lang)
            page = relink(page, slug, lang)
            out = SITE / lang / slug / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page, encoding="utf-8")
    sitemap()
    print(f"{len(APPS)} pages françaises complétées, {len(APPS) * 2} pages EN/ES générées, sitemap à jour")


if __name__ == "__main__":
    main()
