#!/usr/bin/env python3
"""Images de partage (og:image) : une par app et par langue, 1200×630.

Jusqu'au 2026-10-12, les 64 pages partageaient assets/og-studio.png : un lien
vers Rhythm envoyé dans une messagerie ou cité par une IA montrait le logo du
studio. Ce script compose, pour chaque app et chaque langue, une image avec
l'icône, le nom et le sous-titre traduit (clé `<slug>_subtitle` de js/i18n.js),
la rend avec Chrome sans interface puis la convertit en JPEG (sips).

Sortie : assets/og/<slug>-<lang>.jpg. Les pages y sont branchées par
scripts/build_lang_pages.py.
    python3 scripts/build_og.py
"""
import html
import json
import subprocess
import tempfile
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
LANGS = ("fr", "en", "es")
OUT = SITE / "assets/og"

# fond, couleur principale, texte : reprises des thèmes de style.css
PALETTE = {
    "rhythm": ("#FDFAF8", "#C96B8A", "#2D1B24"), "runfree": ("#0D1117", "#FF6B35", "#F0F4F8"),
    "myfoodbook": ("#FDF6F0", "#4A7C7E", "#22312F"), "hydrome": ("#F7FEFF", "#29B6F6", "#1A3A4A"),
    "stockwatch": ("#0D1117", "#16A34A", "#F0F6FC"), "enjoymeal": ("#FAFAF8", "#FF6B35", "#2D2D2D"),
    "chapter": ("#120E14", "#B48CC8", "#F3ECF6"), "nova": ("#0F0E0C", "#C9A45A", "#F2EBD7"),
    "mantrame": ("#FDFAF5", "#7C9B7C", "#2D3A2D"), "lunarest": ("#0A0E1A", "#6B8DE3", "#EEF2FF"),
    "inhale": ("#F4F7FC", "#6B8FB8", "#1B2A3F"), "budgetbrief": ("#071A2B", "#42A5F5", "#EAF4FD"),
}
FOOT = {"fr": "Gratuit sur l'App Store · myideapp.com", "en": "Free on the App Store · myideapp.com",
        "es": "Gratis en la App Store · myideapp.com"}


def translations():
    src = (SITE / "js/i18n.js").read_text(encoding="utf-8")
    js = src + "\nprocess.stdout.write(JSON.stringify(TRANSLATIONS));"
    return json.loads(subprocess.check_output(["node", "-e", js], text=True))


def card(app, lang, sub):
    bg, primary, text = PALETTE[app["slug"]]
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{(SITE / 'css/fonts.css').as_uri()}">
<style>
  html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
  body{{font-family:Inter,system-ui,sans-serif;background:{bg};color:{text};position:relative}}
  .glow{{position:absolute;inset:0;background:radial-gradient(circle at 85% 20%,{primary}55,transparent 55%),
        radial-gradient(circle at 10% 100%,{primary}33,transparent 50%)}}
  .wrap{{position:relative;display:flex;align-items:center;gap:64px;height:100%;padding:0 96px;box-sizing:border-box}}
  img{{width:240px;height:240px;border-radius:54px;box-shadow:0 24px 60px rgba(0,0,0,.28);flex:none}}
  h1{{font-size:92px;line-height:1;margin:0 0 22px;font-weight:800;letter-spacing:-.03em}}
  p{{font-size:40px;line-height:1.25;margin:0;font-weight:600;color:{primary}}}
  .foot{{position:absolute;left:96px;bottom:48px;font-size:26px;font-weight:600;opacity:.7}}
</style></head><body><div class="glow"></div>
<div class="wrap"><img src="{(SITE / 'assets' / app['slug'] / 'icon.png').as_uri()}">
<div><h1>{html.escape(app['name'])}</h1><p>{html.escape(sub)}</p></div></div>
<div class="foot">{html.escape(FOOT[lang])}</div></body></html>"""


def main():
    T = translations()
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for app in APPS:
            for lang in LANGS:
                sub = T[lang].get(app["slug"] + "_subtitle") or T["en"][app["slug"] + "_subtitle"]
                page = Path(tmp) / f"{app['slug']}-{lang}.html"
                page.write_text(card(app, lang, sub), encoding="utf-8")
                png = Path(tmp) / f"{app['slug']}-{lang}.png"
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                "--allow-file-access-from-files", "--virtual-time-budget=2000",
                                "--window-size=1200,630", f"--screenshot={png}", page.as_uri()],
                               check=True, capture_output=True)
                jpg = OUT / f"{app['slug']}-{lang}.jpg"
                subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
                                str(png), "--out", str(jpg)], check=True, capture_output=True)
    print(f"{len(APPS) * len(LANGS)} images dans {OUT.relative_to(SITE)}/")


if __name__ == "__main__":
    main()
