# Annuaire Bamako

Application web qui rassemble **adresses et numéros de téléphone des infrastructures publiques du District de Bamako** : hôpitaux et cliniques, ministères et institutions, universités et écoles, mairies, commissariats, ambassades, eau/électricité/télécoms, culture.

- Recherche instantanée (insensible aux accents), filtres par catégorie et par commune
- Appel en un clic, WhatsApp quand le numéro est un mobile, itinéraire Google Maps
- Carte OpenStreetMap des fiches géolocalisées
- Bandeau des numéros d'urgence toujours visible
- Fonctionne hors-ligne une fois la page chargée (service worker), installable sur mobile (PWA)
- **Chaque fiche affiche sa source et sa date** — aucune coordonnée inventée

## Lancer en local

Aucune dépendance, aucun build. Il faut juste un serveur HTTP (le `fetch` du JSON ne marche pas en `file://`) :

```bash
python -m http.server 8000
```

Puis ouvrir http://localhost:8000

## Déployer sur Vercel

Le dépôt est un site statique : Vercel le déploie sans configuration.

```bash
npm i -g vercel
vercel
```

Ou, depuis l'interface Vercel : **Add New… → Project → importer le dépôt GitHub → Deploy**.
Laisser « Framework Preset » sur **Other**, ne rien mettre en Build Command, et `.` en Output Directory.

Après le premier déploiement, renseignez votre dépôt dans `scripts/build_data.py` (champ `meta.repo`,
par exemple `"votre-compte/annuaire-bamako"`) puis relancez `python scripts/build_data.py` : les boutons
« Signaler » de chaque fiche ouvriront alors une issue GitHub pré-remplie.

## Structure

```
index.html                 page unique
styles.css  app.js         interface (thème clair/sombre automatique)
sw.js  manifest.webmanifest cache hors-ligne + installation mobile
data/annuaire.json         base publiée, générée — NE PAS ÉDITER À LA MAIN
data/curated.json          fiches vérifiées à la main (prioritaires) ← éditer ici
data/raw/malipages.json    fiches brutes collectées
data/raw/geocache.json     coordonnées GPS mises en cache
scripts/scrape_malipages.py collecte
scripts/geocode.py          géocodage Nominatim (OpenStreetMap)
scripts/build_data.py       fusion + nettoyage → data/annuaire.json
```

## Mettre à jour les données

```bash
python scripts/scrape_malipages.py data/raw/malipages.json   # recollecte (optionnel)
python scripts/build_data.py                                  # reconstruit data/annuaire.json
python scripts/geocode.py                                     # complète les coordonnées manquantes
python scripts/build_data.py                                  # réinjecte les coordonnées
```

### Corriger ou ajouter une fiche

Éditez **`data/curated.json`** puis relancez `python scripts/build_data.py`.

```jsonc
{
  "id": "mon-identifiant",
  "name": "Nom complet de la structure",
  "acronym": "SIGLE",                    // facultatif
  "category": "sante",                   // voir la liste "categories" du même fichier
  "type": "Hôpital public — urgences 24h/24",
  "quartier": "Médina Coura",
  "commune": "Commune II",
  "address": "Médina Coura, BP 267, Bamako",
  "phones": [{ "number": "20230780", "label": "standard" }],  // 8 chiffres, sans +223
  "email": "…", "website": "https://…",
  "source": { "name": "Site officiel", "url": "https://…" },
  "replaces": ["HOPITAL GABRIEL TOURE"]  // écrase la fiche brute correspondante
}
```

Le champ `replaces` fusionne la fiche brute dans la vôtre : les numéros trouvés ailleurs sont conservés,
votre adresse et votre source font autorité.

## Provenance et fiabilité des données

| Source | Usage |
|---|---|
| [Ministère de la Santé — numéros d'urgence](https://www.sante.gov.ml/index.php?option=com_content&view=article&id=187&Itemid=111) | numéros courts nationaux (122, 101, 111, 36061) |
| Sites officiels (hopitaldumali.ml, chme-luxembourg.ml, somagep.ml, edmsa.ml, dgi.gouv.ml, coursupreme.ml, koulouba.ml…) | fiches vérifiées de `data/curated.json` |
| [Malipages](https://www.malipages.com/annuaire/) | gros de l'annuaire (ministères, ambassades, écoles, cliniques…) |
| [Nominatim / OpenStreetMap](https://nominatim.openstreetmap.org/) | coordonnées GPS |

**Limites à connaître :**

- Une partie des fiches Malipages date de 2017 ; la date de la fiche est affichée sur chaque carte.
- **124 fiches sur 386 sont géolocalisées.** Un point n'est accepté que s'il est dans Bamako, que sa
  nature concorde (un institut n'est pas un ministère), que le sigle éventuel ouvre le nom du lieu, et
  que le nom recoupe suffisamment celui de la fiche. Les fiches sans correspondance sûre n'ont pas de
  marqueur : le bouton « Itinéraire » bascule alors sur une recherche par nom et adresse dans Google
  Maps, plutôt que d'afficher une position fausse. Ce choix coûte quelques marqueurs corrects, mais
  un marqueur faux envoie quelqu'un au mauvais endroit.
- Pour épingler un point vous-même, ajoutez `"lat"` et `"lng"` à la fiche dans `data/curated.json` :
  ils ont priorité sur le géocodage automatique.
- Les rattachements aux communes sont déduits du quartier ; quelques-uns peuvent être approximatifs.
- **En urgence vitale, composez les numéros courts nationaux** plutôt qu'un standard qui peut avoir changé.

## Licence

Le code est libre d'usage. Les coordonnées proviennent de sources publiques citées fiche par fiche ;
les données cartographiques sont © contributeurs OpenStreetMap (ODbL).
