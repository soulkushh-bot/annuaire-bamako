---
name: Danaya
description: L'annuaire de Bamako qui dit d'où vient chaque numéro
colors:
  mali-vert: "#14B53A"
  mali-or: "#FCD116"
  mali-rouge: "#CE1126"
  vert-action: "#0a7d3c"
  vert-encre: "#075c2c"
  vert-tendre: "#e2f6e7"
  or-encre: "#6b4e00"
  or-tendre: "#fff5cc"
  rouge-urgence: "#CE1126"
  rouge-tendre: "#fbe6e7"
  fond: "#f6f7f4"
  surface: "#ffffff"
  encre: "#17201b"
  encre-douce: "#5d6b63"
  filet: "#e2e6e1"
typography:
  display:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  title:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.4
  data:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 700
    fontFeature: "tabular-nums"
rounded:
  sm: "6px"
  md: "10px"
  lg: "12px"
  xl: "14px"
  full: "999px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
components:
  pilule-urgence:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.rouge-urgence}"
    typography: "{typography.data}"
    rounded: "{rounded.full}"
    padding: "0 14px"
    height: "44px"
  bouton-appel:
    backgroundColor: "{colors.vert-tendre}"
    textColor: "{colors.vert-encre}"
    typography: "{typography.data}"
    rounded: "{rounded.md}"
    padding: "0 13px"
    height: "44px"
  bouton-appel-hover:
    backgroundColor: "{colors.vert-action}"
    textColor: "{colors.surface}"
  puce-filtre:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.encre}"
    rounded: "{rounded.full}"
    padding: "7px 13px"
  puce-filtre-active:
    backgroundColor: "{colors.mali-vert}"
    textColor: "#05300f"
  ligne-fiche:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.encre}"
    rounded: "{rounded.lg}"
    padding: "7px 11px"
  etiquette-categorie:
    backgroundColor: "{colors.vert-tendre}"
    textColor: "{colors.vert-encre}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "3px 9px"
---

# Design System: Danaya

## Overview

**Creative North Star: "Le registre de garde"**

Le cahier posé sur le comptoir d'un poste de garde, la nuit : on l'ouvre, on trouve le numéro, on
appelle. Rien n'y est là pour séduire. Chaque ligne porte une écriture différente selon qui l'a
inscrite et quand, et c'est justement ce qui permet de savoir à quelle entrée se fier. Danaya
transpose cela : une liste dense, un numéro composable par ligne, et la provenance de chaque
information écrite à côté d'elle plutôt qu'enfouie dans une mention légale.

Le drapeau malien n'est pas un ornement posé sur ce registre, c'est sa reliure. Ses trois champs
coiffent chaque écran en un filet de 4 px, la marque les reprend en trois bandes verticales, et
le rouge redescend immédiatement dessous pour porter le bandeau des urgences — le drapeau lu de
haut en bas au lieu de gauche à droite. Le vert tient les actions et la marque « vérifié », l'or
tient les repères, le rouge n'est jamais dépensé ailleurs que sur l'urgence.

La densité prime sur le confort visuel : sept fiches par écran de téléphone, pas une. Le système
refuse la mise en page marketing — pas d'image d'en-tête, pas de bloc de persuasion, pas de
carte pleine largeur pour dire une seule chose.

**Key Characteristics:**
- Tricolore structurel, jamais décoratif : trois champs égaux, jamais un dégradé, jamais un lavis.
- Pile de polices système : aucune police web, aucun téléchargement avant le premier rendu.
- Liste dense de lignes dépliables ; la carte détaillée est le dépliage, pas la liste.
- Le rouge est réservé à l'urgence et n'apparaît nulle part ailleurs.
- Chaque fiche porte sa source et sa date à l'écran.

## Colors

Les trois couleurs du drapeau malien servent de source ; les variantes assombries prennent le
relais partout où la couleur devient de l'encre, parce que le vert et l'or du drapeau ne tiennent
pas 4,5:1 sur fond clair.

### Primary
- **Vert du Mali** (#14B53A) : aplats d'état actif — puce de filtre sélectionnée, bouton Carte
  enclenché — et tiers gauche du filet tricolore et de la marque. Toujours avec une encre très
  sombre (#05300f), jamais du blanc : le blanc y tombe à 2,3:1.
- **Vert d'action** (#0a7d3c) : fonds pleins portant du texte blanc, survol des numéros.
- **Vert encre** (#075c2c) : texte vert sur fond clair — numéros composables, marque « vérifié »,
  horaires.
- **Vert tendre** (#e2f6e7) : fond des numéros au repos et des étiquettes de catégorie.

### Secondary
- **Or du Mali** (#FCD116) : tiers central du filet et de la marque, trait de 64 × 5 px sous le
  titre de la page, contour de la fiche atteinte depuis un marqueur de carte. Jamais en texte.
- **Or encre** (#6b4e00) : le seul texte autorisé sur un fond or.

### Tertiary
- **Rouge du Mali** (#CE1126) : fond plein du bandeau d'urgence et couleur des numéros courts
  dans leurs pilules blanches. En thème sombre il s'assombrit à #a3151f pour que le blanc y reste
  à 14,9:1.

### Neutral
- **Fond** (#f6f7f4 clair / #0f1412 sombre) : le champ de la page, très légèrement chaud.
- **Surface** (#ffffff / #171d1a) : lignes de fiches, en-tête, champs de saisie.
- **Encre** (#17201b / #eef2ee) : texte courant, 15,5:1 sur le fond.
- **Encre douce** (#5d6b63 / #9fb0a6) : métadonnées, sources, libellés de champs.
- **Filet** (#e2e6e1 / #263029) : bordures, séparateurs, silhouettes de chargement.

### Named Rules

**La Règle du Rouge Réservé.** Le rouge ne sert qu'à l'urgence. Aucune erreur de formulaire,
aucun bouton de suppression, aucun accent décoratif ne le reprend. Un utilisateur qui voit du
rouge sur cet écran doit pouvoir en déduire qu'il s'agit d'un numéro à composer en cas de danger.

**La Règle des Trois Champs.** Le tricolore apparaît toujours en trois champs de largeur égale
aux valeurs exactes du drapeau, jamais en dégradé progressif, jamais en aplat partiel, jamais
réordonné. Deux emplacements seulement : le filet de 4 px en tête de l'en-tête collant, et la
marque de 26 px.

**La Règle de l'Encre Sombre sur le Vert Vif.** Tout fond en #14B53A porte une encre à #05300f.
Le blanc sur le vert du drapeau donne 2,3:1 et a déjà été livré une fois par erreur.

## Typography

**Police unique :** pile système (`system-ui`, `-apple-system`, `Segoe UI`, `Roboto`,
`Helvetica Neue`, Arial, sans-serif).

**Character:** aucune police n'est téléchargée. Ce n'est pas un renoncement mais une décision de
performance : le public consulte sur des téléphones modestes et des connexions lentes, et une
interface de tâche est bien servie par la police que l'appareil dessine déjà le mieux. Le
caractère vient de la hiérarchie et de la couleur, pas d'un dessin de lettre.

### Hierarchy
- **Display** (700, 2rem, 1.15, −0.02em) : le titre de la page, une fois. Suivi du trait d'or.
- **Title** (600, 0.9375rem, 1.25) : le nom d'une structure dans la liste, tronqué à deux lignes.
- **Body** (400, 1rem, 1.5) : texte d'accompagnement et prose de la section « À propos ».
- **Label** (600, 0.75rem) : étiquettes de catégorie, marque « vérifié », libellés de champs.
- **Data** (700, 0.9375rem, `tabular-nums`) : tous les numéros de téléphone et les compteurs.

### Named Rules

**La Règle de l'Échelle Fermée.** Sept pas fixes en rem (0.75 / 0.8438 / 0.9375 / 1 / 1.125 /
1.5 / 2), aucune taille littérale dans la feuille de style, aucun `clamp()`. Une version
antérieure déclarait ces jetons puis laissait coexister dix-neuf tailles improvisées.

**La Règle des Chiffres Alignés.** Toute suite de chiffres qu'un lecteur peut être amené à
comparer ou à recopier — numéros, fax, compteurs, horaires — est en `tabular-nums`.

## Layout

Conteneur de 1120 px au maximum, moins 32 px de marges (24 px sous 560 px). La liste est une
colonne unique de lignes séparées de 6 px, quelle que soit la largeur : la densité passe par la
hauteur des lignes, pas par des colonnes.

Chaque ligne est une grille de trois colonnes — `1fr auto auto` : le bloc nom et métadonnées, le
numéro composable, le chevron. Le bloc nom se tronque à deux lignes ; la ligne de métadonnées ne
se replie jamais (catégorie, marque de vérification, commune restent sur une ligne, la commune
absorbant la troncature).

**Responsive :** le changement est structurel, jamais typographique. Sous 560 px, la bande de
catégories défile horizontalement au lieu de s'empiler, la marque « vérifié » se réduit à sa
coche et les étiquettes de catégorie rapetissent. Sous 430 px, les pilules d'urgence resserrent
leur marge intérieure mais **gardent leur libellé** : le bandeau défile alors horizontalement,
en l'annonçant par un dégradé de bord et une accroche au défilement.

L'en-tête est collant à 0 ; le bandeau d'urgence est collant juste dessous, à une hauteur
**mesurée au chargement** et non codée en dur, parce que le contenu de l'en-tête peut changer.

**Rythme :** plus d'espace au-dessus d'un titre qu'en dessous. Groupes serrés (6–8 px),
séparations généreuses (16–24 px).

### Named Rules

**La Règle des Sept Fiches.** Un écran de téléphone de 812 px doit montrer au moins cinq fiches
sous les filtres. La grille de cartes n'en montrait qu'une : c'est ce qui l'a fait remplacer.

**La Règle du Mot Conservé.** Densifier ne veut pas dire abréger. Un numéro d'urgence garde son
libellé à toutes les largeurs, et une étiquette abrégée dans la liste doit revenir en toutes
lettres dans le dépliage. Le public inclut des Maliens de l'extérieur rentrés au pays, pour qui
« 122 » ou « Admin. » ne vont pas de soi. Quand la place manque, on fait défiler en l'annonçant,
on ne retire pas le mot.

## Elevation & Depth

Système presque plat, à un seul niveau. Une ombre unique et discrète (`0 1px 2px
rgba(20,30,25,.06), 0 6px 20px -12px rgba(20,30,25,.25)`) détache les surfaces du fond ; elle
porte à la fois un décalage et un flou, jamais un halo coloré sans décalage. La profondeur vient
surtout du contraste entre le fond (#f6f7f4) et les surfaces (#ffffff), et des filets de 1 px.

### Shadow Vocabulary
- **Ombre de surface** (`0 1px 2px rgba(20,30,25,.06), 0 6px 20px -12px rgba(20,30,25,.25)`) :
  lignes de fiches, en-tête, champ de recherche, silhouettes de chargement. La seule du système.
- **Halo de survol d'urgence** (`0 0 0 3px rgba(255,255,255,.45)`) : uniquement sur les pilules
  blanches posées sur le rouge, où une ombre portée ne se verrait pas.

### Named Rules

**La Règle de l'Ombre Unique.** Une seule ombre dans tout le système. Un besoin de hiérarchie se
résout par la couleur de fond ou un filet, jamais par une deuxième ombre.

## Shapes

Angles arrondis progressifs selon la taille : 6 px pour les étiquettes, 10 px pour les boutons
d'appel, 12 px pour les lignes de fiches, 14 px pour le champ de recherche, et le plein arrondi
(999 px) pour tout ce qui est pilule — puces de filtre, boutons fantômes, numéros d'urgence.

Les bordures sont des filets de 1 px en `--filet`. Une ligne dépliée passe sa bordure au vert
d'action. **Aucune bordure latérale colorée** de plus de 1 px sur une ligne ou une alerte.

Les icônes sont dessinées en SVG, trait de 2 px, extrémités et jointures arrondies, jamais des
glyphes Unicode ni des émojis.

## Components

### Bandeau d'urgence *(composant signature)*
La bande rouge pleine juste sous l'en-tête, collante à la hauteur mesurée de celui-ci. Elle
porte le libellé « URGENCES » en capitales blanches puis les pilules blanches des quatre numéros
vitaux (122, 101, 111, 36061) en chiffres rouges de 1,125 rem, hauteur 44 px. Les quatre numéros
secondaires sont derrière un bouton « +4 autres » translucide. Le libellé du service reste affiché à toutes les
largeurs — « 122 » seul ne dit rien à qui rentre au pays après des années — et le bandeau défile
donc sur petit écran, en l'annonçant. Ce composant ne se met jamais en retrait : il n'entre pas dans le défilement, ne se réduit pas, ne se colore pas autrement.

### Ligne de fiche *(composant signature)*
Un `<details>` — dépliage sans JavaScript, clavier et lecteurs d'écran gratuits — regroupé par
`name="fiche"` pour n'en ouvrir qu'une à la fois. En tête : le nom (deux lignes maximum), une
ligne de métadonnées sur un seul rang (étiquette de catégorie courte, coche « vérifié »,
commune), le premier numéro en bouton d'appel, et un chevron qui pivote de 180°. Le dépliage
révèle le type, l'adresse, les horaires, tous les numéros avec leurs libellés et WhatsApp sur les
mobiles, le fax, les actions et la ligne de source. Composer un numéro ne déplie pas la fiche.

### Boutons
- **Forme :** plein arrondi (999 px) pour les boutons fantômes, 10 px pour les boutons d'appel,
  8 px pour les actions du dépliage.
- **Bouton d'appel :** fond vert tendre, texte vert encre, 44 px de haut, chiffres alignés.
  Survol : fond vert d'action, texte blanc. Actif : vert encre.
- **Bouton fantôme :** transparent, filet de 1 px, 38 px. Survol : fond vert tendre. Enclenché :
  fond vert du drapeau, encre #05300f, graisse 600.
- **Focus :** anneau de 2 px en vert d'action, décalé de 2 px, **sans rayon imposé** — l'anneau
  suit la géométrie de l'élément.

### Puces de filtre
Pilules blanches à filet, avec le compte en chiffres alignés dans un `<small>` plus pâle.
Sélectionnée : fond vert du drapeau, encre très sombre. Sous 560 px, la bande défile
horizontalement, sans barre de défilement visible.

### Champ de recherche
Filet de 2 px, rayon 14 px, ombre de surface, icône loupe à gauche en `--encre-douce`. Au focus,
le filet passe au vert d'action. Le bouton d'effacement est un disque de 34 px avec une croix
dessinée en SVG.

### Repère de distance
Pastille or à encre sombre, chiffres alignés, visible seulement sous le tri « Les plus proches de
moi ». C'est la seule donnée de la ligne qui dépend de l'endroit où se trouve le lecteur. Si la
position est refusée ou indisponible, le tri revient au nom et le compteur le dit : la liste ne
reste jamais muette.

### Silhouettes de chargement
Huit blocs à la forme d'une ligne : deux barres grises (46 % et 28 % de large), rayon 12 px,
hauteur minimale 56 px. Pulsation d'opacité de 1,4 s, désactivée sous `prefers-reduced-motion`.
Jamais de rond tournant au milieu du contenu.

## Do's and Don'ts

### Do:
- **Do** garder le bandeau d'urgence collant, rouge plein, et ses cibles à 44 px. C'est le seul
  élément dont la disponibilité est vitale.
- **Do** mesurer la hauteur de l'en-tête au chargement et la publier dans `--head-h` : une
  valeur codée en dur s'est déjà désynchronisée en ajoutant une ligne dans l'en-tête.
- **Do** poser une encre à #05300f sur tout fond en vert du drapeau.
- **Do** passer chaque taille de police par un jeton `--t-*`.
- **Do** dessiner les icônes en SVG au trait de 2 px.
- **Do** thématiser ce que dessine le navigateur : sélection, curseur, anneaux de focus,
  ascenseurs, décalage de soulignement, chiffres tabulaires.

### Don't:
- **Don't** utiliser le rouge ailleurs que sur l'urgence.
- **Don't** écrire du blanc sur #14B53A ni sur #FCD116 : 2,3:1 et 1,3:1.
- **Don't** remettre la liste en grille de cartes de taille identique : à 375 px elle ne montrait
  qu'une fiche sur 386.
- **Don't** imposer un `border-radius` dans la règle de focus : il écrase la forme des pilules.
- **Don't** charger une police web ni une bibliothèque avant le premier rendu. Leaflet n'est tiré
  qu'à l'ouverture de la carte.
- **Don't** rendre les 386 fiches d'un coup : la liste se rend par lots de 60.
- **Don't** substituer un glyphe Unicode à une icône.
- **Don't** ajouter une seconde ombre au système.
