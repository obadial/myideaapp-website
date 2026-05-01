# Design System — MyIdeaApp Website

## Principes

- **Cohérence** : chaque app garde sa propre identité visuelle, le studio unifie l'ensemble
- **Minimalisme** : pas de surcharge, chaque élément a un rôle
- **Mobile-first** : layout pensé pour mobile, enrichi sur desktop
- **Accessibilité** : contrastes WCAG AA, focus visible, labels aria

---

## Palettes de couleurs

### Studio (landing page)
| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg` | `#08091A` | Fond principal |
| `--bg2` | `#0D1028` | Fond secondaire |
| `--surface` | `#12152E` | Cartes, surfaces |
| `--surface2` | `#1A1F3D` | Surfaces secondaires |
| `--border` | `rgba(255,255,255,0.07)` | Bordures |
| `--text` | `#E8EEFF` | Texte principal |
| `--text2` | `#8892B0` | Texte secondaire |
| `--text3` | `#4A5578` | Texte tertiaire |
| `--accent1` | `#C96B8A` | Accent rose (Rhythm) |
| `--accent2` | `#6B8DE3` | Accent bleu (LunaRest) |

### Rhythm (charte app)
| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg` | `#FDFAF8` | Fond crème |
| `--primary` | `#C96B8A` | Rose principal |
| `--secondary` | `#9B7FB5` | Lavande |
| `--accent` | `#E8A07A` | Pêche |
| `--text` | `#2D1B24` | Texte foncé |
| `--text2` | `#7A5F68` | Texte secondaire |

**Couleurs phases du cycle :**
- Menstruelle : `#C96B8A` (rose)
- Folliculaire : `#7AB5A0` (sauge)
- Ovulation : `#F0B86A` (doré)
- Lutéale : `#9B7FB5` (lavande)

### LunaRest (charte app)
| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg` | `#0A0E1A` | Fond marine très sombre |
| `--primary` | `#6B8DE3` | Bleu principal |
| `--secondary` | `#9B7FE8` | Violet |
| `--accent` | `#FFB347` | Or/ambre |
| `--text` | `#EEF2FF` | Texte clair |
| `--text2` | `#8B9AC4` | Texte secondaire |

---

## Typographie

**Police** : Inter (Google Fonts) — 300, 400, 500, 600, 700, 800, 900

| Usage | Taille | Poids | Lettre-espacement |
|-------|--------|-------|-------------------|
| Titre hero studio | clamp(3.5rem, 10vw, 8rem) | 900 | -0.04em |
| Titre hero app | clamp(2.25rem, 6vw, 3.75rem) | 900 | -0.04em |
| Section title | clamp(1.5rem, 4vw, 2.25rem) | 800 | -0.03em |
| App card name | 2.25rem | 900 | -0.04em |
| Body | 1rem / 1.0625rem | 400 | — |
| Caption | 0.8125rem | 500–600 | +0.02–0.06em |

---

## Composants

### `.navbar`
- Position : `fixed`, top, full width
- Glassmorphism : `backdrop-filter: blur(20px)`
- Hauteur : 64px
- Sur les pages light (Rhythm) : fond crème semi-transparent
- Sur les pages dark : fond `rgba(8,9,26,0.72)`

### `.app-card` (studio landing)
- Coins arrondis `--r-xl` (32px)
- Dégradé d'arrière-plan propre à chaque app
- Halo radial en overlay pseudo-element
- Hover : `translateY(-8px)` + ombre plus prononcée

### `.feature-card`
- Fond `--surface`, bordure `--border`
- Hover : `translateY(-4px)` + glow de la couleur primaire

### `.phone-frame`
- Cadre de téléphone en CSS pur (fond `#1A1A1F`, coins 36px, padding 10px)
- Le 2e frame est décalé de +28px, le 3e de +14px (effet profondeur)

### `.luna-visual`
- Cercles animés en CSS (pulse + expand keyframes)
- Anneaux concentriques avec opacité décroissante
- Icône de l'app au centre

### `.legal-text`
- `h2` : séparateur border-bottom + margin-top `--sp-lg`
- `li::before` : bullet coloré avec `--primary`
- Largeur max 780px (`.container--narrow`)

---

## Animations

| Classe | Comportement |
|--------|-------------|
| `.fade-up` | Démarre à `opacity: 0; translateY(28px)` |
| `.fade-up.visible` | Transition vers `opacity: 1; translateY(0)` |
| `.fade-up-delay-N` | Délai progressif de 0.1s par step |
| `.orb` | Float vertical (8s, ease-in-out infinite) |
| `.stars` | Background-image statique de points blancs |
| `.luna-circle` | Pulse sur `box-shadow` (4s) |
| `.luna-ring` | Expand scale (4s, offset par ring) |

**IntersectionObserver** : `threshold: 0.12` — déclenche l'animation quand 12% de l'élément est visible.

---

## Responsive

| Breakpoint | Changements |
|------------|-------------|
| `< 900px` | About section en 1 colonne ; hero app sans screenshots ; features en 2 colonnes |
| `< 640px` | Hamburger menu ; apps grid en 1 colonne ; features en 1 colonne ; footer en 1 colonne |

---

## Pages légales

- Fond neutre (respecte le thème de l'app)
- Largeur max 780px pour une lecture confortable
- Tabs de langue en haut : montrent/cachent les blocs `.legal-content`
- Sections `h2` avec bordure inférieure pour la lisibilité
- Bullets colorés avec la couleur primaire de l'app
