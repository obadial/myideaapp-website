import json, glob, re, collections, sys
S = sys.argv[1]
R = [x for f in sorted(glob.glob(S + '/audit_part_*.json')) for x in json.load(open(f))]
print(len(R), "rendus\n")
FR = re.compile(r"\b(avec|pour|sans|tes|ton|votre|vos|données|être|télécharger|découvrir|gratuit|appareil|confidentialité|utilisation|mentions|dernière|bientôt|suivi|aucun|aucune|toutes|chaque|ou bien|nous|notre|retour)\b", re.I)
EN = re.compile(r"\b(the|with|your|without|download|privacy|terms|coming soon|learn more|features|every|and)\b", re.I)
ES = re.compile(r"\b(con|para|sin|tus|datos|descargar|privacidad|cada|nuestro|también|aplicación)\b", re.I)
WRONG = {"en": [FR, ES], "es": [FR], "fr": [EN]}
by = collections.defaultdict(list)
for r in R:
    key = (r['page'])
    if r.get('errors'): by['Erreurs JS / console'].append(f"{r['page']} [{r['lang']},{r['w']}] {r['errors'][:3]}")
    if r.get('failed'): by['Ressources en erreur'].append(f"{r['page']} [{r['lang']}] {r['failed'][:3]}")
    if r.get('overflow', 0) > 2 and r['w'] == 390: by['Débordement horizontal mobile'].append(f"{r['page']} [{r['lang']}] +{r['overflow']}px {r.get('wide')}")
    if r.get('brokenImg'): by['Images cassées'].append(f"{r['page']} {r['brokenImg']}")
    if r.get('noAlt') and r['lang'] == 'fr' and r['w'] == 1280: by['Images sans alt'].append(f"{r['page']} {r['noAlt'][:3]}")
    if r.get('i18nMissing'): by['Clé i18n affichée brute'].append(f"{r['page']} [{r['lang']}] {r['i18nMissing']}")
    if r.get('lang') and r.get('lang') != r['lang'] and not r['page'].startswith(('guides/en', 'guides/es', 'guides/fr', 'mycookbook', 'nova/support')): by['html lang ≠ langue choisie'].append(f"{r['page']} choisi={r['lang']} html={r.get('lang')}")
    if r['w'] == 1280 and r['lang'] == 'fr' and len(r.get('h1', [])) != 1 and not r['page'].startswith(('mycookbook', 'nova/support')): by['h1 visibles ≠ 1'].append(f"{r['page']} {r.get('h1')}")
    if r['w'] == 1280 and r['page'].split('/')[0] not in ('guides',) and r['lang'] in WRONG:
        lines = []
        for line in (r.get('text') or '').split('\n'):
            l = line.strip()
            if len(l) < 4 or 'English' in l or 'Español' in l or 'Français' in l: continue
            hits = sum(len(rx.findall(l)) for rx in WRONG[r['lang']])
            if hits >= (1 if len(l) < 40 else 2): lines.append(l[:110])
        if lines: by[f"Texte pas dans la langue choisie ({r['lang']})"].append(f"{r['page']}: " + " | ".join(dict.fromkeys(lines))[:600])
for k, v in by.items():
    print(f"## {k} ({len(v)})")
    for x in v: print("  ", x)
    print()
