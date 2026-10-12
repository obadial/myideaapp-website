#!/usr/bin/env python3
"""FAQ visible des 12 pages d'app, en FR / EN / ES.

Jusqu'au 2026-10-12, la FAQ n'existait qu'en français : un visiteur en anglais
ou en espagnol voyait « Questions fréquentes » au milieu d'une page traduite.
Ce script régénère, entre `<!-- faq:start -->` et `<!-- faq:end -->`, un bloc
`data-lang-block` par langue (même mécanisme que l'encadré « En bref »).
Le JSON-LD FAQPage n'est pas touché : il reste en français, langue par défaut
de la page.

Idempotent. Source : data/faq.json.
    python3 scripts/build_faq.py
"""
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = json.loads((SITE / "data/faq.json").read_text(encoding="utf-8"))
LANGS = ("fr", "en", "es")
e = html.escape

ITEM = ('        <details class="faq-item" style="border-bottom:1px solid rgba(128,128,128,0.18);padding:1.15rem 0;">\n'
        '          <summary style="cursor:pointer;font-weight:600;font-size:1.05rem;list-style:none;">{q}</summary>\n'
        '          <p style="margin:.85rem 0 0;opacity:.82;line-height:1.65;">{a}</p>\n'
        '        </details>')
LEGACY = re.compile(r'      <h2 class="section-title fade-up">Questions fréquentes</h2>\s*'
                    r'<div class="faq"[^>]*>.*?\n      </div>', re.S)


def render(items):
    def r(l):
        body = "\n".join(ITEM.format(q=e(i["q"][l], quote=False), a=e(i["a"][l], quote=False)) for i in items)
        return (f'      <div data-lang-block="{l}" lang="{l}">\n'
                f'      <h2 class="section-title">{e(DATA["title"][l])}</h2>\n'
                f'      <div class="faq" style="max-width:760px;margin:2rem auto 0;">\n{body}\n      </div>\n'
                f'      </div>')
    return "<!-- faq:start -->\n" + "\n".join(r(l) for l in LANGS) + "\n      <!-- faq:end -->"


def main():
    for slug, items in DATA["apps"].items():
        p = SITE / slug / "index.html"
        s = p.read_text(encoding="utf-8")
        block = render(items)
        if "<!-- faq:start -->" in s:
            s = re.sub(r"<!-- faq:start -->.*?<!-- faq:end -->", lambda _: block, s, flags=re.S)
        else:
            m = LEGACY.search(s)
            if not m:
                raise SystemExit(f"{slug} : FAQ introuvable")
            old = [html.unescape(q) for q in re.findall(r"<summary[^>]*>(.*?)</summary>", m.group(0))]
            if old != [i["q"]["fr"] for i in items]:
                raise SystemExit(f"{slug} : les questions FR de data/faq.json ne correspondent plus à la page")
            s = s[:m.start()] + "      " + block + s[m.end():]
        p.write_text(s, encoding="utf-8")
    print(f"FAQ régénérée sur {len(DATA['apps'])} pages")


if __name__ == "__main__":
    main()
