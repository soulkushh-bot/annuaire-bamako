# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

HTML, CSS et JavaScript statiques, sans étape de construction ni framework. Le choix est
contraint par le public visé : le site doit rester consultable sur un téléphone modeste et une
connexion lente, et déployable sur un hébergement statique gratuit. Les données sont un unique
fichier JSON produit par des scripts Python à part, jamais servi depuis une base de données.

## Users

L'habitant de Bamako qui a besoin d'un numéro ou d'une adresse **maintenant** : appeler les
pompiers, trouver le CSRéf de sa commune pour un accouchement, joindre le service des impôts,
savoir où se situe le commissariat de son arrondissement. Il est souvent sur un téléphone
Android d'entrée de gamme, sur une connexion lente ou coupée, parfois dans l'urgence.

**Le Malien de l'extérieur rentré au pays**, explicitement nommé par le propriétaire du projet.
Il connaît le Mali mais plus la ville au quotidien : les quartiers ont bougé, les numéros courts
ne lui sont pas familiers, il ne sait pas forcément que 122 est celui des pompiers. Conséquence
directe sur l'interface : **les abréviations qui vont de soi pour un habitant ne vont pas de soi
pour lui.** Une compression qui gagne de la place en retirant un mot doit être vérifiée contre
ce public avant d'être retenue.

Publics secondaires : les nouveaux arrivants et visiteurs cherchant une ambassade ou un hôpital,
et les agents publics qui ont besoin des coordonnées d'une autre administration.

## Product Purpose

Rassembler en un seul endroit consultable les coordonnées des infrastructures publiques du
District de Bamako — santé, institutions, administrations, écoles et universités, mairies,
police, ambassades, eau, électricité, télécoms, culture — et permettre d'appeler ou de s'y rendre
en quelques secondes.

Réussite : quelqu'un qui cherche un numéro le trouve et le compose sans avoir à quitter la page,
y compris sans réseau, et sait s'il peut s'y fier.

## Positioning

Ce que les annuaires maliens existants ne font pas : **dire ce qui a été vérifié et ce qui ne
l'a pas été.** Chaque fiche affiche sa source et sa date. 61 fiches sur 386 ont été recoupées à
la main sur des sites officiels et portent une marque « vérifié » ; les autres viennent d'un
annuaire public dont beaucoup d'entrées datent de 2017, et la date est affichée telle quelle.
Quand aucun numéro fiable n'a été trouvé, la fiche l'écrit au lieu d'afficher un numéro plausible.

Le nom **Danaya** — « la confiance » en bambara — nomme cet engagement.

## Operating Context

- Consultation debout, dans la rue ou dans une cour, sur un écran de 375 px de large.
- Réseau intermittent : le service worker garde l'annuaire entier consultable hors connexion.
- Usage d'urgence : les numéros courts nationaux doivent être composables à tout instant, sans
  recherche préalable et sans défilement.
- Les gens désignent les lieux par commune (« Commune V ») et par quartier (« Torokorobougou »),
  pas par adresse postale.

## Capabilities and Constraints

**Ce que l'application fait :** recherche insensible aux accents et par tranches de numéro,
filtres par catégorie et par commune, tri (nom, catégorie, vérification récente, vérifiées
d'abord, **les plus proches de moi** par géolocalisation), appel direct, WhatsApp sur les numéros
mobiles, itinéraire Google Maps, carte Leaflet des fiches géolocalisées, partage, signalement d'erreur vers les issues GitHub, fonctionnement
hors-ligne, installation sur l'écran d'accueil.

**Contraintes techniques :** page unique statique ; aucune dépendance chargée avant le premier
rendu (Leaflet n'est tiré qu'à l'ouverture de la carte) ; pas de police web ; interface en
français.

**Numérotation malienne :** 8 chiffres, mobiles commençant par 5, 6, 7 ou 9 — seuls ceux-là
reçoivent un bouton WhatsApp. Les numéros courts (3 à 5 chiffres) ne sont joignables que depuis
le Mali.

**Découpage administratif — fait à connaître :** la loi n°2023-005 du 13 mars 2023 a supprimé les
communes du District de Bamako au profit de sept arrondissements sans personnalité juridique,
sous un maire unique. L'application conserve les Communes I à VI parce que c'est le repère
employé au quotidien et celui qui figure sur les adresses ; la section « À propos » explique la
nuance. Ne pas « corriger » ce choix sans décision explicite.

## Brand Commitments

- **Nom : Danaya.** Bambara pour « la confiance ». Sous-titre : « Annuaire de Bamako ».
- **Auteur : Souleymane Coulibaly**, affiché dans l'en-tête, le pied de page et la métadonnée
  `author`. La paternité du projet doit rester visible.
- **Couleurs du drapeau malien** — vert, or, rouge — comme signature visuelle assumée, décision
  explicite du propriétaire du projet.
- **Langue : français**, celle de l'administration malienne.

## Evidence on Hand

- `data/annuaire.json` — 386 fiches publiées, générées, ne jamais éditer à la main.
- `data/curated.json` — 61+ fiches vérifiées à la main, avec source et date. **C'est ici qu'on
  corrige.**
- `data/raw/malipages.json` — collecte brute de l'annuaire Malipages, avec la date de chaque fiche.
- `data/raw/geocache.json` — coordonnées GPS validées par des règles strictes (nature de
  l'établissement, position du sigle, recoupement du nom).

**Sources officielles utilisées :** ministère de la Santé (numéros d'urgence), sites propres des
institutions (hopitaldumali.ml, chme-luxembourg.ml, somagep.ml, edmsa.ml, dgi.gouv.ml,
coursupreme.ml, koulouba.ml, usttb-edu.org), arrêté du ministère de la Sécurité du 31 août 2022
(renommage des commissariats), OpenStreetMap (positions).

**Absences à ne pas combler par invention :** les CSRéf des Communes II et III n'ont pas de
téléphone vérifiable en ligne ; l'annuaire officiel des structures de santé de l'OIM refuse tout
téléchargement hors navigateur ; 325 fiches sur 386 n'ont jamais été recoupées ; 261 n'ont pas de
position GPS ; les horaires ne sont connus que pour 5 fiches. Ces manques sont affichés, pas
masqués.

## Product Principles

1. **Densifier ne veut pas dire abréger.** Gagner de la place en retirant un mot se paie chez
   celui qui ne connaît pas déjà la réponse. Les numéros d'urgence gardent leur libellé à toutes
   les largeurs ; la liste peut abréger une étiquette à condition que le dépliage la rétablisse
   en toutes lettres.
2. **Un manque affiché vaut mieux qu'un numéro inventé.** Sur un hôpital ou un commissariat, une
   erreur envoie quelqu'un au mauvais endroit un jour où ça compte.
3. **La source et la date font partie de la donnée**, pas d'une mention légale. Elles s'affichent
   sur la fiche.
4. **Les numéros d'urgence sont hors concours** : toujours à l'écran, jamais derrière une
   recherche, jamais derrière un défilement, cible tactile pleine.
5. **Le premier écran doit tenir sur un téléphone lent.** Rien ne bloque le rendu initial ; ce
   qui n'est pas indispensable est chargé à la demande.
6. **On corrige dans `curated.json`, jamais dans le fichier publié**, et toute correction porte
   une source.

## Accessibility & Inclusion

Contrastes vérifiés au-dessus de 4,5:1 dans les deux thèmes, y compris sur les états actifs et le
bandeau d'urgence. Cibles tactiles de 44 px sur les appels, WhatsApp et les urgences. Navigation
au clavier avec anneaux de focus visibles qui ne déforment pas la géométrie des éléments.
`aria-live` limité au compteur de résultats. Mouvement respectant `prefers-reduced-motion`. La
coche « vérifié », réduite à une icône sur écran étroit, garde son sens par `aria-label`.
