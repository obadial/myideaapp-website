# Audit de rendu dans Chrome (oct. 2026)

Outils de contrôle, pas de génération : ils ouvrent les pages dans un vrai Chrome
(protocole DevTools, Node ≥ 20 avec `--experimental-websocket`) et signalent ce
qu'un visiteur verrait. À lancer avant chaque push d'un changement visible.

Pré-requis : `python3 -m http.server 8765` à la racine du site.

```bash
# 1. Rendu de toutes les pages × FR/EN/ES × bureau (1280) / mobile (390)
find . -name "*.html" -not -path "./.git/*" -not -path "./docs/*" \
  | sed 's|^\./||;s|index.html$||;s|^$|./|' | sort > /tmp/pages.txt
mkdir -p /tmp/audit && OUT=/tmp/audit/audit_part_a.json PORT=9333 \
  xargs node --experimental-websocket scripts/audit/render_audit.mjs http://localhost:8765 < /tmp/pages.txt
#    (≈ 12 s par page : découper la liste en 4 lots avec des PORT différents
#     et des OUT audit_part_*.json pour aller 4× plus vite)

# 2. Synthèse : erreurs JS, ressources 404, images cassées, débordement mobile,
#    clés i18n brutes, texte dans la mauvaise langue
python3 scripts/audit/analyse.py /tmp/audit

# 3. Captures avec une langue de navigateur donnée (stockage vidé)
node --experimental-websocket scripts/audit/shot.mjs /tmp fr-FR 1280 1000 http://localhost:8765/rhythm/
```

Limites connues : `analyse.py` compare le texte à la langue *choisie* ; pour les
pages à langue fixe (`data-lang-static`), comparer à `lang` (langue réelle).
Le titre « Mentions légales » reste en français : page à ne pas modifier.
