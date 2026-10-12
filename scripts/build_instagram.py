#!/usr/bin/env python3
"""Page « Sur Instagram » : les vrais posts du studio, affichés dans des écrans d'iPhone.

Demande de Lucas (2026-10-12) : un rendu joli où l'on voit les posts réels du
studio comme sur l'app Instagram, mis à jour automatiquement.

- Données : data/instagram.json, écrit chaque jour par scripts/fetch_instagram.py
  (GitHub Actions, .github/workflows/instagram.yml) depuis l'API Graph de Meta.
- Les visuels sont des copies légères hébergées sur le site : la page ne charge
  rien depuis Instagram (pas de traceur Meta, pas de bannière cookies).
- Tant qu'il n'y a aucun post, la page n'est pas générée (jamais de faux posts).
- Pas de compteur de « j'aime » : on n'affiche que ce que l'API fournit vraiment.

    /instagram/   /en/instagram/   /es/instagram/
    python3 scripts/build_instagram.py [--data fichier.json] [--out dossier]
"""
import argparse
import datetime
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_guides as G  # noqa: E402
import site_shell  # noqa: E402

SITE = G.SITE
BASE = G.BASE
LANGS = G.LANGS
APPS = {a["slug"]: a for a in json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]}
PATHS = {"fr": "/instagram/", "en": "/en/instagram/", "es": "/es/instagram/"}
e = html.escape
MONTHS = G.MONTHS

TXT = {
    "title": {"fr": "MyIdeApp sur Instagram : les posts de nos 12 apps", "en": "MyIdeApp on Instagram: posts from our 12 apps",
              "es": "MyIdeApp en Instagram: las publicaciones de nuestras 12 apps"},
    "desc": {"fr": "Les derniers posts Instagram des apps MyIdeApp (Rhythm, RunFree, HydroMe, Nova…), mis à jour chaque jour.",
             "en": "The latest Instagram posts from MyIdeApp's apps (Rhythm, RunFree, HydroMe, Nova…), updated daily.",
             "es": "Las últimas publicaciones de Instagram de las apps de MyIdeApp (Rhythm, RunFree, HydroMe, Nova…), actualizadas a diario."},
    "h1": {"fr": ["Sur", "Instagram"], "en": ["On", "Instagram"], "es": ["En", "Instagram"]},
    "intro": {"fr": "Conseils, coulisses et nouveautés : chaque app a son compte. Voici leurs derniers posts, mis à jour chaque jour.",
              "en": "Tips, behind the scenes and what's new: each app has its own account. Here are their latest posts, updated every day.",
              "es": "Consejos, entre bastidores y novedades: cada app tiene su cuenta. Estas son sus últimas publicaciones, actualizadas cada día."},
    "latest": {"fr": ["Les derniers", "posts"], "en": ["Latest", "posts"], "es": ["Últimas", "publicaciones"]},
    "accounts": {"fr": ["Nos", "comptes"], "en": ["Our", "accounts"], "es": ["Nuestras", "cuentas"]},
    "follow": {"fr": "Suivre", "en": "Follow", "es": "Seguir"},
    "see": {"fr": "Voir sur Instagram", "en": "View on Instagram", "es": "Ver en Instagram"},
    "reel": {"fr": "Reel", "en": "Reel", "es": "Reel"},
    "updated": {"fr": "Mis à jour le {d}", "en": "Updated {d}", "es": "Actualizado el {d}"},
    "about": {"fr": "Sur Instagram", "en": "On Instagram", "es": "En Instagram"},
}

HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
COMMENT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 1 1-3.2-6.4A8 8 0 0 1 20 12zm0 0v7l-3-2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
SEND = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 3 3 10l7 3 3 7 8-17zM10 13l11-10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
SAVE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>'


def human_date(iso, lang):
    return G.human_date(iso[:10], lang)


def caption(text, n=110):
    text = re.sub(r"\s+", " ", text or "").strip()
    text = re.sub(r"(#\w+\s*)+$", "", text).strip()  # hashtags de fin : bruit à l'écran
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def phone(post, slug, lang):
    """Un écran d'iPhone qui reprend l'interface d'un post Instagram."""
    app = APPS[slug]
    user = app["instagram"]
    reel = post.get("type") == "VIDEO"
    badge = f'<span class="ig-phone__reel">{PLAY}{e(TXT["reel"][lang])}</span>' if reel else ""
    return f"""        <a class="ig-phone" href="{e(post['permalink'])}" rel="noopener" target="_blank" aria-label="{e(app['name'])} — {e(TXT['see'][lang])}">
          <span class="ig-phone__island"></span>
          <span class="ig-phone__screen">
            <span class="ig-phone__head"><img src="/assets/{slug}/icon-192.png" alt="" width="30" height="30" loading="lazy"><strong>{e(user)}</strong><span class="ig-phone__follow">{e(TXT['follow'][lang])}</span></span>
            <span class="ig-phone__media"><img src="/{e(post['image'])}" alt="" loading="lazy" decoding="async">{badge}</span>
            <span class="ig-phone__actions">{HEART}{COMMENT}{SEND}<span class="ig-phone__save">{SAVE}</span></span>
            <span class="ig-phone__caption"><strong>{e(user)}</strong> {e(caption(post.get('caption')))}</span>
            <span class="ig-phone__date">{e(human_date(post['timestamp'], lang))}</span>
          </span>
        </a>"""


def page(data, lang):
    accounts = {s: a for s, a in data["accounts"].items() if a.get("posts") and s in APPS}
    latest = sorted(((p, s) for s, a in accounts.items() for p in a["posts"]), key=lambda x: x[0]["timestamp"], reverse=True)[:8]
    alternates = {l: BASE + PATHS[l] for l in LANGS}
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": TXT["title"][lang], "url": BASE + PATHS[lang],
           "inLanguage": lang, "isPartOf": {"@id": BASE + "/#organization"},
           "about": [{"@type": "SoftwareApplication", "name": APPS[s]["name"], "sameAs": f"https://www.instagram.com/{APPS[s]['instagram']}/"}
                     for s in accounts]}]
    out = G.head(lang, TXT["title"][lang], TXT["desc"][lang], BASE + PATHS[lang], alternates, "studio", ld)
    out = out.replace('content="article"', 'content="website"', 1)
    phones = "\n".join(phone(p, s, lang) for p, s in latest)
    cards = []
    for s, a in accounts.items():
        thumbs = "".join(f'<a href="{e(p["permalink"])}" rel="noopener" target="_blank"><img src="/{e(p["image"])}" alt="" loading="lazy"></a>'
                         for p in a["posts"][:3])
        cards.append(f"""        <div class="ig-account">
          <a class="ig-account__head" href="https://www.instagram.com/{APPS[s]['instagram']}/" rel="noopener" target="_blank">
            <span class="site-footer__ig-icon"><img src="/assets/{s}/icon-192.png" alt="" width="28" height="28" loading="lazy"><span class="site-footer__ig-badge">{site_shell.IG_GLYPH}</span></span>
            <span class="site-footer__ig-text"><strong>{e(APPS[s]['name'])}</strong><small>@{e(APPS[s]['instagram'])}</small></span>
            <span class="ig-account__follow">{e(TXT['follow'][lang])}</span>
          </a>
          <div class="ig-account__grid">{thumbs}</div>
        </div>""")
    updated = TXT["updated"][lang].format(d=human_date(data["updated"], lang))
    body = f"""
  <main class="guide about instagram">
    <div class="container guide__inner">
      <p class="guide__crumbs"><a href="/">MyIdeApp</a> › {e(TXT['about'][lang])}</p>
      <h1 class="guide__title">{site_shell_two_tone(TXT['h1'][lang])}</h1>
      <p class="guide__intro">{e(TXT['intro'][lang])}</p>

      <section>
        <h2>{site_shell_two_tone(TXT['latest'][lang])}</h2>
        <div class="ig-phones">
{phones}
        </div>
      </section>

      <section>
        <h2>{site_shell_two_tone(TXT['accounts'][lang])}</h2>
        <div class="ig-accounts">
{chr(10).join(cards)}
        </div>
        <p class="guide__checked">{e(updated)}</p>
      </section>
    </div>
  </main>
"""
    return out + "\n" + G.nav(lang, alternates, active=None) + body + G.footer(lang)


def site_shell_two_tone(parts):
    hl, rest = parts
    return f'<span class="tt-hl">{e(hl)}</span> {e(rest)}'.rstrip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(SITE / "data/instagram.json"))
    ap.add_argument("--out", default=str(SITE))
    args = ap.parse_args()
    path = Path(args.data)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"accounts": {}}
    if not any(a.get("posts") for a in data.get("accounts", {}).values()):
        print("Aucun post Instagram dans les données : page non générée")
        return
    for lang in LANGS:
        out = Path(args.out) / PATHS[lang].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(data, lang), encoding="utf-8")
    sm_path = SITE / "sitemap.xml"
    sm = sm_path.read_text(encoding="utf-8")
    day = data["updated"][:10]
    entries = "\n".join(f"  <url>\n    <loc>{BASE}{PATHS[l]}</loc>\n    <lastmod>{day}</lastmod>\n"
                        f"    <changefreq>daily</changefreq>\n    <priority>0.5</priority>\n  </url>" for l in LANGS)
    block = f"  <!-- instagram:start -->\n{entries}\n  <!-- instagram:end -->"
    if "<!-- instagram:start -->" in sm:
        sm = re.sub(r"  <!-- instagram:start -->.*?<!-- instagram:end -->", lambda _: block, sm, flags=re.S)
    else:
        sm = sm.replace("</urlset>", block + "\n\n</urlset>")
    if Path(args.out) == SITE:
        sm_path.write_text(sm, encoding="utf-8")
    print(f"Sur Instagram : 3 pages ({sum(len(a.get('posts', [])) for a in data['accounts'].values())} posts)")


if __name__ == "__main__":
    main()
