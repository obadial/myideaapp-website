# CLAUDE.md — MyIdeApp Website

Site vitrine statique du studio **MyIdeApp**. Aucun build, aucun framework — HTML/CSS/JS pur déployé sur GitHub Pages.

## TODO

- [ ] **Migrer vers un nom de domaine custom** (ex. `myideapp.com`)
  - Ajouter un fichier `CNAME` à la racine du repo
  - Configurer les DNS : CNAME `www` → `obadial.github.io` + 4 enregistrements A vers les IPs GitHub Pages
  - Activer "Enforce HTTPS" dans Settings → Pages
  - Mettre à jour les URLs dans App Store Connect pour Rhythm et LunaRest

## Architecture

### Fichiers clés

| Fichier | Rôle |
|---------|------|
| `css/style.css` | Tous les styles. Themes via `[data-theme]` sur `<body>`. |
| `js/i18n.js` | Objet `TRANSLATIONS` FR/EN/ES + moteur `I18n.apply(lang)`. |
| `js/main.js` | Init scroll animations, tabs légaux, menu mobile, navbar scroll. |
| `index.html` | Studio landing (dark theme). |
| `rhythm/index.html` | Page Rhythm (theme clair rose/lavande). |
| `lunarest/index.html` | Page LunaRest (theme sombre bleu/violet). |
| `*/privacy.html` | Pages légales avec onglets FR/EN/ES. |
| `*/terms.html` | Pages légales avec onglets FR/EN/ES. |

## Système de thèmes

Chaque page déclare son thème sur `<body data-theme="...">` :

| Valeur | Usage | Couleurs principales |
|--------|-------|----------------------|
| `studio` | Landing page | Fond très sombre `#08091A`, accents rose + bleu |
| `rhythm` | Page Rhythm | Fond crème `#FDFAF8`, rose `#C96B8A`, lavande `#9B7FB5` |
| `lunarest` | Page LunaRest | Fond marine `#0A0E1A`, bleu `#6B8DE3`, violet `#9B7FE8` |
| `enjoymeal` | Page EnjoyMeal | Fond chaud `#FAFAF8`, orange `#FF6B35`, vert `#4CAF50` |
| `legal-rhythm` | Pages légales Rhythm | Même charte que `rhythm` |
| `legal-lunarest` | Pages légales LunaRest | Même charte que `lunarest` |
| `legal-enjoymeal` | Pages légales EnjoyMeal | Même charte que `enjoymeal` |

Toutes les couleurs utilisent des **CSS custom properties** (`--bg`, `--text`, `--primary`, etc.)  
→ Modifier un theme : changer uniquement le bloc `[data-theme="..."]` dans `style.css`.

## Internationalisation (i18n)

- **Clés dans le HTML** : `<span data-i18n="studio_tagline">...</span>`
- **Texte par défaut** dans le HTML = français (fallback si JS désactivé)
- **Ajout d'une traduction** : ajouter la clé dans les 3 objets (`fr`, `en`, `es`) dans `js/i18n.js`
- **Langue sauvegardée** : `localStorage.mia_lang`

### Ajouter une langue (ex. DE)
1. Ajouter un objet `de: { ... }` dans `TRANSLATIONS` dans `i18n.js`
2. Ajouter `<button class="lang-btn" data-lang-btn="de">DE</button>` dans chaque navbar
3. Ajouter `<div class="legal-content" data-legal-content="de">` dans chaque page légale
4. Ajouter `<button class="legal-tab" data-legal-tab="de">Deutsch</button>` dans les tabs

## Pages légales

Structure HTML dans `privacy.html` et `terms.html` :

```html
<!-- Tabs de langue -->
<div class="legal-lang-tabs">
  <button class="legal-tab" data-legal-tab="fr">Français</button>
  <button class="legal-tab" data-legal-tab="en">English</button>
</div>

<!-- Contenu par langue (affiché/masqué par main.js) -->
<div class="legal-content" data-legal-content="fr">
  <span class="legal-date">Dernière mise à jour : ...</span>
  <div class="legal-text">
    <h2>1. Section</h2>
    <p>Texte...</p>
  </div>
</div>
```

**⚠️ Important** : La logique JS dans `initLegalTabs()` (main.js) active automatiquement le tab correspondant à la langue courante du site. Si la langue n'a pas de contenu légal, le premier tab s'affiche.

## Ajouter une nouvelle app

1. Copier `rhythm/` → `nouvellapp/`
2. Remplacer les assets dans `assets/nouvellapp/`
3. Dans `index.html` de la nouvelle app : adapter le `data-theme`, les couleurs, le contenu
4. Ajouter une carte dans `index.html` (studio landing)
5. Ajouter les clés i18n (`nouvellapp_*`) dans `js/i18n.js`
6. Créer des pages légales `privacy.html` et `terms.html` avec les textes corrects

## Commandes utiles

```bash
# Aperçu local (Python)
python3 -m http.server 8080
# ou
npx serve .

# Init git + GitHub
git init
git add .
git commit -m "feat: initial website"
gh repo create myideaapp-website --public --source=. --remote=origin --push

# Activer GitHub Pages (via gh CLI)
gh api repos/:owner/myideaapp-website/pages --method POST \
  --field source[branch]=main --field source[path]=/
```

## URLs Apple App Store Connect

Après déploiement GitHub Pages :

- **Rhythm Privacy** : `https://<user>.github.io/myideaapp-website/rhythm/privacy.html`
- **Rhythm Terms** : `https://<user>.github.io/myideaapp-website/rhythm/terms.html`
- **LunaRest Privacy** : `https://<user>.github.io/myideaapp-website/lunarest/privacy.html`
- **LunaRest Terms** : `https://<user>.github.io/myideaapp-website/lunarest/terms.html`
- **EnjoyMeal Privacy** : `https://<user>.github.io/myideaapp-website/enjoymeal/privacy.html`
- **EnjoyMeal Terms** : `https://<user>.github.io/myideaapp-website/enjoymeal/terms.html`

## Conventions

- Pas de commentaires dans le code sauf pour les sections majeures
- CSS : BEM-like (`block__element--modifier`)
- JS : ES6+, pas de dépendances externes
- HTML : sémantique, attributs `lang`, `aria-label`
- Images : `loading="lazy"` sur toutes les images non-hero
