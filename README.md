# MyIdeApp Website

Site vitrine du studio **MyIdeApp** hébergeant les pages légales (RGPD) de Rhythm et LunaRest.  
Déployé sur **GitHub Pages** — aucun build, aucune dépendance.

## Structure

```
myideaapp-website/
├── index.html              # Studio landing page
├── rhythm/
│   ├── index.html          # Page app Rhythm
│   ├── privacy.html        # Politique de confidentialité Rhythm  ← URL Apple
│   └── terms.html          # Conditions d'utilisation Rhythm      ← URL Apple
├── lunarest/
│   ├── index.html          # Page app LunaRest
│   ├── privacy.html        # Politique de confidentialité LunaRest ← URL Apple
│   └── terms.html          # Conditions d'utilisation LunaRest     ← URL Apple
├── css/
│   └── style.css           # Tous les styles (themes par data-theme)
├── js/
│   ├── i18n.js             # Traductions FR/EN/ES + moteur de langue
│   └── main.js             # Animations, tabs légaux, menu mobile
└── assets/
    ├── rhythm/
    │   ├── icon.png
    │   └── screenshots/    # 4 captures App Store
    └── lunarest/
        ├── icon.png
        └── hero.png
```

## Déploiement GitHub Pages

1. Créer un repo GitHub (public) : `myideaapp-website`
2. Push ce dossier sur `main`
3. Settings → Pages → Source : `main` / `/ (root)` → Save
4. URL : `https://<username>.github.io/myideaapp-website/`

### URLs à renseigner dans App Store Connect

| App | Document | URL |
|-----|----------|-----|
| Rhythm | Privacy Policy | `https://<username>.github.io/myideaapp-website/rhythm/privacy.html` |
| Rhythm | Terms | `https://<username>.github.io/myideaapp-website/rhythm/terms.html` |
| LunaRest | Privacy Policy | `https://<username>.github.io/myideaapp-website/lunarest/privacy.html` |
| LunaRest | Terms | `https://<username>.github.io/myideaapp-website/lunarest/terms.html` |

## Langues

Le sélecteur FR/EN/ES est présent sur toutes les pages.  
La préférence est sauvegardée dans `localStorage` (`mia_lang`).  
Détection automatique de la langue du navigateur au premier chargement.

## Ajouter une app

1. Dupliquer `rhythm/` → `newapp/`
2. Adapter les couleurs CSS dans `<style>` de chaque page
3. Ajouter les clés i18n dans `js/i18n.js` (sections `newapp_*`)
4. Ajouter la carte dans `index.html`

## Modifier les textes légaux

Les textes légaux sont en HTML pur dans les fichiers `privacy.html` et `terms.html` de chaque app.  
Chaque langue est un `<div class="legal-content" data-legal-content="fr|en|es">`.  
Pas de rebuild nécessaire — modifier le HTML directement.

## Tech stack

- HTML5 sémantique
- CSS custom properties (themes par `data-theme`)
- Vanilla JS (ES6+)
- Google Fonts (Inter)
- Pas de framework, pas de build step
