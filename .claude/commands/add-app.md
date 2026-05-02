# Ajouter une nouvelle app sur le site MyIdeApp

Ce skill guide l'ajout complet d'une nouvelle app au site vitrine MyIdeApp.

## Ce que tu dois fournir

Avant de commencer, demande à l'utilisateur les informations suivantes si elles ne sont pas déjà fournies :

1. **Nom de l'app** (ex. `EnjoyMeal`) — slug URL déduit automatiquement en minuscules sans espaces
2. **Thème** : `light` (fond clair, comme Rhythm) ou `dark` (fond sombre, comme LunaRest)
3. **Couleur primaire** (hex, ex. `#FF6B35`)
4. **Couleur secondaire** (hex, ex. `#4CAF50`)
5. **Catégorie** (ex. `Nutrition & Bien-être`)
6. **Tagline FR/EN/ES** (ex. `Mange avec plaisir, vis en équilibre.`)
7. **Sous-titre FR/EN/ES** (ex. `Suivi nutritionnel bienveillant`)
8. **Description FR/EN/ES** (2-3 phrases)
9. **6 fonctionnalités** avec emoji, titre et description (FR/EN/ES)
10. **Chemin vers l'icône** (PNG, ex. `../assets/[slug]/icon.png`)
11. **Email de contact** pour les pages légales
12. **Textes légaux** (privacy + terms, FR/EN/ES) — si non fournis, créer des textes génériques adaptés à l'app

Si l'app est un projet Flutter/Dart voisin, propose de lire automatiquement `lib/core/constants/app_colors.dart` et `lib/core/constants/legal_texts.dart` pour extraire couleurs et textes légaux.

## Étapes d'implémentation

### 1. Copier l'icône
```bash
cp [source]/assets/images/app_icon.png assets/[slug]/icon.png
```

### 2. Créer `[slug]/index.html`
Partir du template LunaRest (dark) ou Rhythm (light) selon le thème choisi.
- Remplacer toutes les occurrences du nom de l'app de référence
- Adapter les couleurs dans le `<style>` inline
- Adapter le bloc hero (visual animé ou screenshots)
- Adapter les 6 feature cards
- Mettre à jour le footer pour lister les 3+ apps

### 3. Créer `[slug]/privacy.html` et `[slug]/terms.html`
Partir des templates `rhythm/privacy.html` et `rhythm/terms.html`.
- Remplacer le thème `legal-rhythm` → `legal-[slug]`
- Mettre à jour tous les textes FR/EN/ES avec le vrai contenu légal

### 4. Mettre à jour `css/style.css`
Ajouter dans l'ordre :
```css
/* ─── [APPNAME] Theme */
[data-theme="[slug]"] { /* variables couleurs */ }
[data-theme="legal-[slug]"] { /* variables couleurs légales */ }
/* logo-text gradient */
/* lang-btn.active couleur */
/* app-hero__orb couleur */
/* app-hero background */
/* app-card--[slug] styles */
```

### 5. Mettre à jour `js/i18n.js`
Ajouter dans les 3 blocs `fr`, `en`, `es` :
- `[slug]_chip`, `[slug]_tagline`, `[slug]_subtitle`, `[slug]_description`
- `[slug]_feat_title`, `[slug]_feat{1-6}_title`, `[slug]_feat{1-6}_desc`
- `[slug]_legal_title`, `[slug]_legal_desc`
- `footer_privacy_[slug]`, `footer_terms_[slug]`

Mettre aussi à jour `studio_apps_subtitle` (compter le bon nombre d'apps).

### 6. Mettre à jour `index.html` (studio landing)
- Navbar desktop : ajouter `<a href="[slug]/">[AppName]</a>`
- Navbar mobile : idem
- Apps grid : ajouter une `<a class="app-card app-card--[slug] ...">` après la dernière card
- Footer apps : ajouter `<a href="[slug]/">[AppName]</a>`
- Footer légal : ajouter liens privacy + terms avec `data-i18n`

### 7. Mettre à jour les footers des pages existantes
Dans `rhythm/index.html`, `lunarest/index.html`, et toutes les pages `[existingapp]/index.html` :
- Ajouter `<a href="../[slug]/">[AppName]</a>` dans la section footer apps

### 8. Mettre à jour `CLAUDE.md`
- Ajouter le nouveau thème dans le tableau des thèmes
- Ajouter les URLs légales dans la section "URLs Apple App Store Connect"

## Notes importantes

- **Textes légaux** : toujours utiliser les textes officiels fournis par l'app. Si aucun texte, créer des CGU et politique de confidentialité génériques mais adaptées au type d'app (tracker de santé, app de bien-être, etc.)
- **Pas de screenshots** : si aucun screenshot n'est disponible, utiliser un visual animé CSS (anneaux concentriques avec couleurs de l'app + icône centrale), comme dans `lunarest/index.html`
- **Theme light** : fond clair, overrides navbar/mobile-nav dans le `<style>` inline de la page, comme Rhythm
- **Theme dark** : fond sombre, pas besoin d'override navbar (le dark est le défaut CSS), comme LunaRest
