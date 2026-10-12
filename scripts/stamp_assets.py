#!/usr/bin/env python3
"""Ajoute une empreinte de version (?v=…) aux liens CSS et JS de toutes les pages.

Pourquoi (2026-10-12) : après une mise à jour, des visiteurs (et Lucas) voyaient
encore l'ancien menu « Apps / À propos » : le navigateur gardait l'ancien
js/i18n.js en cache. L'empreinte dépend du contenu du fichier : dès qu'il change,
l'adresse change et le navigateur télécharge la nouvelle version.

À lancer en dernier, après tous les autres scripts. Idempotent.
    python3 scripts/stamp_assets.py
"""
import hashlib
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
ASSETS = ["css/style.css", "css/fonts.css", "js/i18n.js", "js/main.js"]


def main():
    stamps = {a: hashlib.sha1((SITE / a).read_bytes()).hexdigest()[:8] for a in ASSETS}
    pattern = re.compile(r'((?:href|src)="(?:\.\./|/)*(' + "|".join(re.escape(a) for a in ASSETS) + r'))(?:\?v=[0-9a-f]+)?"')
    changed = 0
    for page in SITE.rglob("*.html"):
        if {"scripts", "docs", ".git"} & set(page.relative_to(SITE).parts):
            continue
        s = page.read_text(encoding="utf-8")
        t = pattern.sub(lambda m: f'{m.group(1)}?v={stamps[m.group(2)]}"', s)
        if t != s:
            page.write_text(t, encoding="utf-8")
            changed += 1
    print(f"empreintes posées ({', '.join(f'{a}={h}' for a, h in stamps.items())}) sur {changed} pages modifiées")


if __name__ == "__main__":
    main()
