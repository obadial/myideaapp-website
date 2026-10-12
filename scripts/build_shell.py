#!/usr/bin/env python3
"""Pose l'habillage commun (scripts/site_shell.py) sur les pages statiques du studio.

- index.html                : pied de page commun
- contact.html              : barre du studio + pied de page commun
- suppression-compte.html   : barre du studio (remplace la « navbar minimale ») + pied de page
- mentions-legales.html     : idem — seul l'habillage change, jamais le texte légal

Blocs entre `<!-- shell:nav:* -->` et `<!-- shell:footer:* -->`. Idempotent.
    python3 scripts/build_shell.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_shell  # noqa: E402

SITE = site_shell.SITE
PAGES = {
    "index.html": {"nav": ""},
    "contact.html": {"nav": "contact"},
    "suppression-compte.html": {"nav": ""},
    "mentions-legales.html": {"nav": ""},
}


def put(page, name, content, fallback):
    start, end = f"<!-- shell:{name}:start -->", f"<!-- shell:{name}:end -->"
    block = f"{start}\n{content}\n  {end}"
    if start in page:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, page, flags=re.S)
    m = re.search(fallback, page, flags=re.S)
    if not m:
        raise SystemExit(f"{name} : point d'insertion introuvable")
    return page[:m.start()] + block + page[m.end():]


def main():
    for name, conf in PAGES.items():
        p = SITE / name
        s = p.read_text(encoding="utf-8")
        s = put(s, "footer", site_shell.footer_multi(), r"  <footer class=\"footer\">.*?</footer>")
        if conf["nav"] is not None:
            nav = site_shell.nav_multi(conf["nav"] or None)
            # Ancienne « navbar minimale » remplacée, ou barre ajoutée en tête de page.
            s = put(s, "nav", nav, r"(?:  <!-- ─── Navbar minimale ─+ -->\n)?  <nav class=\"navbar[^\"]*\">.*?</nav>"
                    if re.search(r'<nav class="navbar[" ]', s) and "shell:nav" not in s else r"(?<=<body data-theme=\"studio\">\n)")
        # Accueil : l'ancien menu mobile (apps par catégorie) est remplacé par le
        # menu « burger » de la barre commune.
        s = re.sub(r"\n  <div class=\"mobile-nav\">.*?\n  </div>\n", "\n", s, count=1, flags=re.S)
        if "<!-- shell:ig:start -->" in s:
            s = put(s, "ig", f'        <div class="site-footer__igs">{site_shell.instagram_links()}</div>', r"$^")
        p.write_text(s, encoding="utf-8")
    print(f"habillage commun posé sur {len(PAGES)} pages")


if __name__ == "__main__":
    main()
