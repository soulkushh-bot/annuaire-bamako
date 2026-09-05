"""Construit data/annuaire.json à partir de :
  - data/curated.json            fiches vérifiées à la main (prioritaires)
  - data/raw/malipages.json      fiches brutes de l'annuaire Malipages (scripts/scrape_malipages.py)
  - data/raw/geocache.json       coordonnées GPS (scripts/geocode.py), facultatif

Usage : python scripts/build_data.py
"""
import json, re, os, unicodedata, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)

# ---------------------------------------------------------------- utilitaires
def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", fold(s)).strip("-")
    return s[:80]

# La source Malipages est en capitales sans accents : on restaure les accents des mots courants.
ACCENTS = {
    "cite": "cité", "cites": "cités", "ministere": "ministère", "ministeres": "ministères", "ecole": "école",
    "ecoles": "écoles", "sante": "santé", "liberte": "liberté", "developpement": "développement", "superieur": "supérieur",
    "superieure": "supérieure", "superieures": "supérieures", "universite": "université", "universites": "universités",
    "lycee": "lycée", "faculte": "faculté", "facultes": "facultés", "medical": "médical", "medicale": "médicale",
    "medicales": "médicales", "medicaux": "médicaux", "medecine": "médecine", "medina": "Médina", "generale": "générale",
    "general": "général", "generales": "générales", "republique": "république", "economique": "économique",
    "economiques": "économiques", "economie": "économie", "education": "éducation", "etat": "État", "energie": "énergie",
    "energies": "énergies", "elevage": "élevage", "peche": "pêche", "hoteliere": "hôtelière", "etrangeres": "étrangères",
    "cooperation": "coopération", "exterieur": "extérieur", "integration": "intégration", "defense": "défense",
    "prive": "privé", "privee": "privée", "prives": "privés", "privees": "privées", "reference": "référence",
    "aeroport": "aéroport", "senou": "Sénou", "dravela": "Dravéla", "toure": "Touré", "keita": "Keïta",
    "hopital": "hôpital", "hopitaux": "hôpitaux", "prevoyance": "prévoyance", "impots": "impôts", "regional": "régional",
    "regionale": "régionale", "regulation": "régulation", "marche": "marché", "marches": "marchés",
    "elections": "élections", "delegation": "délégation", "delegations": "délégations", "societe": "société",
    "propriete": "propriété", "geologie": "géologie", "collectivites": "collectivités", "etage": "étage",
    "assemblee": "assemblée", "aerienne": "aérienne", "secretariat": "secrétariat", "academie": "académie",
    "numerique": "numérique", "securite": "sécurité", "metiers": "métiers", "batiment": "bâtiment",
    "batiments": "bâtiments", "comptabilite": "comptabilité", "ingenierie": "ingénierie", "appliquee": "appliquée",
    "appliquees": "appliquées", "reconciliation": "réconciliation", "etudes": "études", "decentralisation": "décentralisation",
    "cohesion": "cohésion", "energetique": "énergétique", "bibliotheque": "bibliothèque", "qualite": "qualité",
    "epuration": "épuration", "donnees": "données", "caractere": "caractère", "independante": "indépendante",
    "telecommunications": "télécommunications", "experimentation": "expérimentation", "geographique": "géographique",
    "vegetaux": "végétaux", "oeuvres": "œuvres", "francais": "français", "francaise": "française", "veterinaire": "vétérinaire",
    "systeme": "système", "systemes": "systèmes", "energetiques": "énergétiques", "numeros": "numéros", "specialise": "spécialisé",
    "securises": "sécurisés", "operationnelle": "opérationnelle", "strategie": "stratégie", "unite": "unité",
    "controle": "contrôle", "interet": "intérêt", "execution": "exécution", "creation": "création", "cle": "clé",
    "electrique": "électrique", "electricite": "électricité", "telesante": "télésanté", "telephonie": "téléphonie",
    "pediatrie": "pédiatrie", "pediatrique": "pédiatrique", "maternite": "maternité", "chirurgie": "chirurgie",
    "hotel": "hôtel", "cheikh": "Cheikh", "guinee": "Guinée", "algerie": "Algérie", "egypte": "Égypte",
    "etats": "États", "unis": "Unis", "bresil": "Brésil", "senegal": "Sénégal", "nigeria": "Nigeria",
    "royame": "Royaume", "royaume": "Royaume", "cotedivoire": "Côte d'Ivoire", "arabie": "Arabie",
    "prefecture": "préfecture", "tresor": "trésor", "recette": "recette", "depot": "dépôt", "reseau": "réseau",
    "reseaux": "réseaux", "electorale": "électorale", "sacre": "Sacré", "coeur": "Cœur", "avancees": "avancées",
    "integree": "intégrée", "integrees": "intégrées", "renovation": "rénovation", "modernisation": "modernisation",
    "monetaire": "monétaire", "segou": "Ségou", "perfectionnement": "perfectionnement", "securisation": "sécurisation",
    "developpe": "développe", "developpes": "développés", "diplome": "diplôme", "diplomes": "diplômes",
    "interieur": "intérieur", "ferme": "ferme", "elementaire": "élémentaire", "secondaire": "secondaire",
    "professionnel": "professionnel", "specialisee": "spécialisée", "specialisees": "spécialisées",
    "cereales": "céréales", "hydraulique": "hydraulique", "reglementation": "réglementation", "verificateur": "vérificateur",
    "mediateur": "médiateur", "tresorerie": "trésorerie", "penitentiaire": "pénitentiaire", "securites": "sécurités",
    "cres": "CRES", "eleves": "élèves", "etudiants": "étudiants", "ecoliers": "écoliers", "ainee": "aînée",
    "autorite": "autorité", "autorites": "autorités", "activites": "activités", "societes": "sociétés",
    "proprietaire": "propriétaire", "immobiliere": "immobilière", "financiere": "financière", "financieres": "financières",
    "fiscaux": "fiscaux", "carriere": "carrière", "carrieres": "carrières", "matiere": "matière", "matieres": "matières",
    "premiere": "première", "deuxieme": "deuxième", "troisieme": "troisième", "arriere": "arrière", "riviere": "rivière",
    "frontiere": "frontière", "frontieres": "frontières", "etrangere": "étrangère", "etranger": "étranger",
    "communaute": "communauté", "communautaire": "communautaire", "solidarite": "solidarité", "equite": "équité",
    "egalite": "égalité", "proximite": "proximité", "securiser": "sécuriser", "reforme": "réforme", "reformes": "réformes",
    "regime": "régime", "regimes": "régimes", "resultats": "résultats", "reussite": "réussite", "prescolaire": "préscolaire",
    "electronique": "électronique", "electroniques": "électroniques", "informatiques": "informatiques",
    "operateur": "opérateur", "operateurs": "opérateurs", "cooperative": "coopérative", "cooperatives": "coopératives",
    "gerance": "gérance", "generaux": "généraux", "genie": "génie", "hotellerie": "hôtellerie", "theatre": "théâtre",
    "cinema": "cinéma", "musee": "musée", "musees": "musées", "patrimoine": "patrimoine", "bibliotheques": "bibliothèques",
    "meteorologie": "météorologie", "meteo": "Météo", "publicite": "publicité", "conferences": "conférences",
    "conference": "conférence", "independence": "Indépendance", "independance": "Indépendance", "problematique": "problématique",
    "operationnel": "opérationnel", "energetiques": "énergétiques", "priorite": "priorité", "unites": "unités",
    "sanitaire": "sanitaire", "sanitaires": "sanitaires", "veterinaires": "vétérinaires", "elementaires": "élémentaires",
    "numerisation": "numérisation", "telephone": "téléphone", "batisseurs": "bâtisseurs", "cotonniere": "cotonnière",
    "miniere": "minière", "minieres": "minières", "petroliere": "pétrolière", "hoteliers": "hôteliers",
}

ACRONYMS = {"ACI", "BP", "CHU", "RN", "SA", "SARL", "TIC", "VIH", "SIDA", "FED", "BTP", "US", "USA", "UE", "ONU", "UEMOA",
            "OAPI", "CEDEAO", "TSF", "OUA", "CAN", "ENI", "ENA", "ENSUP", "IOTA", "CNOS", "INPS", "CANAM", "AMO", "DGI",
            "PPM", "ORTM", "AMAP", "EDM", "IER", "IGM", "INSTAT", "AGETIC", "ANAC", "ANPE", "APEJ", "CCIM", "CICB", "CMSS",
            "CNDH", "CNPM", "CSA", "DNH", "DNI", "DNCC", "DNGM", "DNUH", "HAC", "FAFPA", "AEDD", "OMH", "ONEF", "OPAM", "OPV",
            "APDP", "AIGE", "DGE", "AMRTP", "ARMDS", "AGEROUTE", "BUMDA", "LCV", "INSP", "USTTB", "ULSHB", "USJPB", "USSGB",
            "UYOB", "FMOS", "FST", "ISA", "FAPH", "FSEG", "ISFRA", "ISPRIC", "ISTAG", "ISFIC", "ISPP", "ISFMI", "UIE", "ITMA",
            "IPR", "IFRA", "CENOU", "CFCT", "CNAM", "CNTS", "HCNLS", "ANAM", "ANTIM", "ONASR", "CMS", "GLA", "HDB", "SIAB",
            "STC", "CDIB", "MSIPC", "ADN", "ADNM", "ANICT", "APEX", "API", "APCAM", "APCMM", "AMANORM", "AMALAN", "ACALAN",
            "AMARAP", "AGEFAU", "AGETIPE", "ANGESEM", "OCLEI", "OFII", "OMA", "CEMAPI", "CECAM", "ONP", "CNR", "ENF",
            "CNREX", "CONFED", "DGDM", "MAECI", "UGP", "GAVI", "ISC", "SUP", "ISIG", "IAM", "IHEM", "ESGB", "ESG", "IUG",
            "INA", "CFP", "IUGB", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "TV", "FM", "DG", "PMU",
            "SNV", "GIZ", "USAID", "PNUD", "UNICEF", "OMS", "FAO", "PAM", "HCR", "OIM", "BCEAO", "BOAD", "BAD", "BM", "FMI",
            "UNESCO", "UNFPA", "ONUSIDA", "CICR", "MSF", "BNDA", "BDM", "BIM", "BMS", "BSIC", "BOA", "SDC", "MGR", "BGV"}
SMALL = {"de", "du", "des", "la", "le", "les", "et", "a", "à", "au", "aux", "en", "pour", "sur", "par", "d", "l", "un", "une",
         "ex", "the", "of", "and", "in", "for"}

def _word(w, first):
    """Met un mot dans la bonne casse et lui rend ses accents."""
    if re.fullmatch(r"\d+(er|e)", w):          # ordinaux déjà normalisés : 10e, 1er
        return w
    up = w.upper()
    if up in ACRONYMS or re.search(r"\d", w) or (len(w) <= 3 and not re.search(r"[AEIOUY]", up)):
        return up
    key = fold(w)
    acc = ACCENTS.get(key)
    if acc and acc[0].isupper():                # nom propre du dictionnaire (Médina, Touré…)
        return acc
    base = acc or (w.capitalize() if (w.isupper() or w[1:].isupper()) else w)
    if key in SMALL and not first:
        return base.lower()
    return base[0].upper() + base[1:]

def smart_case(text):
    """Convertit un libellé TOUT EN MAJUSCULES en casse lisible : accents restaurés, acronymes et chiffres préservés."""
    if not text:
        return ""
    text = text.replace("’", "'").replace("–", "—")
    text = re.sub(r"\b(\d+)\s*[EÈ]?ME\b", r"\1e", text, flags=re.I)   # 10EME -> 10e
    text = re.sub(r"\b1\s*ER\b", "1er", text, flags=re.I)
    out, first = [], True
    for w in re.split(r"([^0-9A-Za-zÀ-ÿ']+)", text):   # sépare la ponctuation des mots
        if not w:
            continue
        if not re.search(r"[0-9A-Za-zÀ-ÿ]", w):
            out.append(w); continue
        m = re.match(r"^([LD])'(.+)$", w, flags=re.I)  # L'ADMINISTRATION -> l'Administration
        if m:
            art = ("L" if first else "l") if m.group(1).upper() == "L" else ("D" if first else "d")
            out.append(art + "'" + _word(m.group(2), False))
        else:
            out.append(_word(w, first))
        first = False
    s = "".join(out)
    s = re.sub(r"\bL' ", "l'", s)
    return s

def phones_from(raw):
    """'+223 20 22 50 92/ 20 22 67 40 / 76 ...' -> ['20225092', '20226740', ...] (8 chiffres) ; garde les numéros courts."""
    if not raw:
        return []
    raw = re.sub(r"[​‌‍]", "", raw)
    res = []
    for part in re.split(r"[/,;]|\bet\b", raw):
        d = re.sub(r"\D", "", part)
        if not d:
            continue
        if d.startswith("223") and len(d) >= 11:
            d = d[3:]
        elif d.startswith("00223"):
            d = d[5:]
        if len(d) == 8:
            res.append(d)
        elif len(d) == 2 and res:  # "20 29 20 04/05" -> variante du dernier groupe
            res.append(res[-1][:-2] + d)
        elif 3 <= len(d) <= 5:
            res.append(d)
    seen, uniq = set(), []
    for n in res:
        if n not in seen:
            seen.add(n); uniq.append(n)
    return uniq

# ------------------------------------------------------------ quartiers -> commune
COMMUNES = {
    "Commune I": ["korofina", "djelibougou", "boulkassoumbougou", "banconi", "fadjiguila", "sotuba", "doumanzana", "sikoroni",
                  "sangarebougou", "dielibougou", "route de koulikoro km 8"],
    "Commune II": ["missira", "niarela", "quinzambougou", "hippodrome", "bagadadji", "medina coura", "bozola", "bakaribougou",
                   "zone industrielle", "tsf", "n'gomi", "cite du niger", "rue titi niare", "grand marche"],
    "Commune III": ["centre commercial", "bamako coura", "darsalam", "dar salam", "ouolofobougou", "badialan", "dravela",
                    "koulouba", "point g", "n'tomikorobougou", "same", "quartier du fleuve", "square patrice lumumba",
                    "cite administrative", "place de la liberte", "avenue de la liberte", "rue baba diarra", "bolibana",
                    "coura bolibana", "ex base", "marche dibida", "avenue moussa travele", "boulevard de l'independence",
                    "avenue de l'yser", "rue charles merieux", "avenue vollenhoven", "route de kati", "route de koulouba"],
    "Commune IV": ["hamdallaye", "hamdalaye", "lafiabougou", "djicoroni", "sebenikoro", "taliko", "lassa", "kalabambougou",
                   "aci 2000", "sibiribougou", "avenue cheick zayed", "place de la can"],
    "Commune V": ["badalabougou", "badala", "quartier mali", "torokorobougou", "baco djicoroni", "bacodjicoroni", "sabalibougou",
                  "daoudabougou", "kalaban coura", "kalabancoura", "garantibougou", "colline du savoir", "cite universitaire",
                  "cite mali univers", "n'torokorobougou"],
    "Commune VI": ["sogoniko", "magnambougou", "faladie", "niamakoro", "banankabougou", "senou", "missabougou", "yirimadio",
                   "yirimadjo", "sokorodji", "dianeguela", "faso kanu", "route de l'aeroport", "halles de bamako", "sirakoro",
                   "corniche du canal"],
    "Kati (hors District)": ["kati", "kalabancoro", "kalaban coro", "kabala", "niamana", "sanankoroba", "baguineda",
                             "kanadjiguila", "moribabougou", "samako"],
}
def guess_commune(addr, quartier=""):
    a = fold(addr + " " + quartier)
    # Djicoroni Para est en Commune IV, Baco Djicoroni en Commune V : tester le plus spécifique d'abord
    if "baco djicoroni" in a or "bacodjicoroni" in a:
        return "Commune V"
    if "kalaban coura" in a or "kalabancoura" in a:
        return "Commune V"
    for com, keys in COMMUNES.items():
        for k in keys:
            if k in a:
                return com
    return ""

def split_addr(addr):
    """'HAMDALLAYE ACI 2000 - RUE 405 PORTE 359 - BP E 423 - BAMAKO' -> (quartier, adresse lisible, ville)."""
    parts = [p.strip() for p in re.split(r"\s+-\s+|\s-\s|\s{2,}-", addr) if p.strip()]
    city = ""
    if parts and fold(parts[-1]) in {"bamako", "kati", "segou", "gao", "kayes", "sikasso", "mopti", "koulikoro", "tombouctou",
                                      "kidal", "bandiagara", "djenne", "koury", "pelengana", "sana", "sanzana", "tessalit",
                                      "sevare", "baguineda", "niamana"}:
        city = parts.pop().title()
    quartier = ""
    if parts and not re.match(r"^(BP|B\.P|RUE|AVENUE|PORTE|IMMEUBLE|ROUTE|BOULEVARD|PLACE|SQUARE|CITE ADMINISTRATIVE)", parts[0], re.I):
        quartier = smart_case(parts[0])
    elif parts and re.match(r"^(PLACE|SQUARE|CITE ADMINISTRATIVE|ROUTE DE KOULOUBA|AVENUE DE LA LIBERTE|COLLINE)", parts[0], re.I):
        quartier = smart_case(parts[0])
    readable = ", ".join(smart_case(p) for p in parts)
    if city:
        readable = f"{readable}, {city}" if readable else city
    return quartier, readable, city

# ------------------------------------------------------------- catégorisation
EXCLUDE = re.compile(r"ASSOCIATION|FEDERATION|PROJET |PROJET$|SYNDICAT|BOURSE DE|PATRONAT|CELLULE|UNITE DE GESTION|"
                     r"CONSEIL REGIONAL|ASSEMBLEE REGIONALE|OFFICE RIZ|MATERNELLE|CRECHE|GARDERIE|BILINGUE|ENGLISH|SPEAK|"
                     r"CODING|MOON LIGHT|PITCHOUNNES|MELI-MELO|LIVING SCHOOL|CARLCARE|TECNO|XIAOMI|INTERCOM|"
                     r"ZIL TELECOM|ALKAN|ATEL SA|TECHNOTEL|SOINS A DOMICILE|SANTE MOBILE|CONFED|SECRETARIAT A L|OFII|"
                     r"^JOURNAL (?!L.ESSOR)|MALIJET|MALIWEB|MALI ?TRIBUNE|OKELEDO|RHHM|JOLIBA|LE JALON|LA VOIX|"
                     r"ICRISAT|CREDOS|SCOFI|MALIDENKO|PRUBA|OPI –|CMTR|"
                     r"DIRECTION REGIONALE DE L.HYDRAULIQUE DE (?!.*BAMAKO)|DIRECTION REGIONALE DE LA SANTE DE|FERLAIT|"
                     r"FENAGROUP|FENASCOM|AMAPEF|APROCA|ARAFD|ASSAFE|AMSS|AMPPF|AMASEF|AMAPROS|AMADECOM|ALPHA-LOG|AJA MALI",
                     re.I)

RULES = [
    ("ambassades", r"AMBASSADE|CONSULAT|HAUT COMMISSARIAT|DELEGATION DE L.UNION EUROPEENNE"),
    ("gouvernement", r"MINISTERE|PRIMATURE|PRESIDENCE|ASSEMBLEE NATIONALE|CONSEIL NATIONAL DE TRANSITION|CONSEIL ECONOMIQUE|"
                     r"MEDIATEUR DE LA REPUBLIQUE|SECRETARIAT GENERAL DU GOUVERNEMENT|COUR CONSTITUTIONNELLE|"
                     r"VERIFICATEUR GENERAL|HAUTE AUTORITE|HAUT CONSEIL"),
    ("justice", r"COUR SUPREME|COUR D.APPEL|TRIBUNAL|ORDRE DES NOTAIRES|ORDRE DES AVOCATS|CECAM|ARBITRAGE"),
    ("securite", r"COMMISSARIAT DE POLICE|GENDARMERIE|PROTECTION CIVILE|SAPEURS|POLICE"),
    ("collectivites", r"^MAIRIE|GRAND BAMAKO"),
    ("sante", r"HOPITAL|CLINIQUE|CENTRE HOSPITALIER|POLYCLINIQUE|CABINET DENTAIRE|CENTRE MEDIC|CSREF|CENTRE DE SANTE|"
              r"LABORATOIRE|BIOLAB|BIOGENE|GROUPE SANTE|CNOS|CNAM|INSP|IOTA|PHARMACIE|ONASR|HCNLS|ANAM|ANTIM|CMS –|"
              r"ORDRE DES PHARMACIENS|ORDRE DES MEDECINS|TRANSFUSION|LUTTE CONTRE LE VIH"),
    ("education", r"UNIVERSIT|INSTITUT SUPERIEUR|INSTITUT PRIVE|INSTITUT DES SCIENCES|INSTITUT SIMON|INSTITUT SUP|"
                  r"^ECOLE|ECOLE NATIONALE|ECOLE NORMALE|ECOLE SUPERIEUR|LYCEE|FACULTE|CENOU|CENTRE DE FORMATION|TECHNOLAB|"
                  r"POLYTECHNI|ACADEMY|SUP.MANAGEMENT|ISFRA|ISPRIC|ISTAG|ISFIC|ISPP|ISFMI|ITMA|SIMPLON|APTECH|CFCT|"
                  r"CENTRE DE PROMOTION DES METIERS|CONSERVATOIRE|INSTITUT NATIONAL DES ARTS|ISC MALI|IAM|IHEM|ESG"),
    ("services", r"ORANGE MALI|MOOV|TELECEL|SOMAGEP|SOMAPEP|EDM|LA POSTE|AEROPORT|GARE|ANAC|METEO|LABORATOIRE NATIONAL DES EAUX"),
    ("medias", r"ORTM|AMAP|L.ESSOR|MAISON DE LA PRESSE|RADIO|TELEVISION"),
    ("culture", r"INSTITUT FRANCAIS|CENTRE CULTUREL|MUSEE|BIBLIOTHEQUE|PALAIS DE LA CULTURE|STADE|CICB|CONFERENCES"),
    ("organisations", r"UEMOA|OAPI|CEDEAO|NATIONS UNIES|PNUD|UNICEF|OMS|BANQUE MONDIALE|BCEAO|BOAD"),
]
def categorize(name, src_cat):
    for cat, rx in RULES:
        if re.search(rx, name, re.I):
            return cat
    return {"ministeres": "gouvernement", "mairies": "collectivites", "cliniques-et-hopitaux": "sante",
            "services-medicaux": "sante", "ecoles-et-universites": "education", "telecom": "services",
            "presse": "medias"}.get(src_cat, "administrations")

TYPES = [
    (r"AMBASSADE", "Ambassade"), (r"CONSULAT", "Consulat"), (r"MINISTERE", "Ministère"), (r"^MAIRIE", "Mairie"),
    (r"COMMISSARIAT", "Commissariat de police"), (r"HOPITAL|CENTRE HOSPITALIER", "Hôpital"), (r"POLYCLINIQUE", "Polyclinique"),
    (r"VETERINAIRE", "Vétérinaire"), (r"CLINIQUE", "Clinique"), (r"CABINET DENTAIRE", "Cabinet dentaire"),
    (r"CABINET MEDICAL", "Cabinet médical"), (r"LABORATOIRE|BIOLAB|BIOGENE", "Laboratoire d'analyses"),
    (r"UNIVERSIT", "Université"), (r"LYCEE", "Lycée"), (r"INSTITUT|ECOLE|ACADEMY|TECHNOLAB|SIMPLON|APTECH", "École / institut"),
    (r"AGENCE", "Agence publique"), (r"DIRECTION", "Direction nationale"), (r"OFFICE", "Office public"),
    (r"AUTORITE", "Autorité de régulation"), (r"CAISSE", "Caisse"), (r"ORDRE DES", "Ordre professionnel"),
    (r"CHAMBRE|ASSEMBLEE PERMANENTE", "Chambre consulaire"), (r"CONSEIL", "Conseil"), (r"COMMISSION", "Commission"),
    (r"COUR ", "Cour"), (r"JOURNAL|PRESSE", "Presse"),
]
def guess_type(name):
    for rx, t in TYPES:
        if re.search(rx, name, re.I):
            return t
    return ""

def split_name(raw_name):
    """'AMRTP – AUTORITE MALIENNE ...' -> ('AMRTP', 'Autorité Malienne ...')."""
    n = raw_name.replace("’", "'").strip()
    parts = re.split(r"\s+[–—-]\s+", n, maxsplit=1)
    if len(parts) == 2 and len(parts[0]) <= 16 and " " not in parts[0].strip() or (len(parts) == 2 and re.fullmatch(r"[A-Z0-9 .\-/&]{2,16}", parts[0])):
        acro, rest = parts[0].strip(), parts[1].strip()
        return acro, smart_case(rest), f"{smart_case(rest)} ({acro})"
    return "", smart_case(n), smart_case(n)

def iso_date(d):
    m = re.match(r"(\d\d)/(\d\d)/(\d{4})", d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""

# ---------------------------------------------------------------------- build
def main():
    curated = json.load(open(P("data", "curated.json"), encoding="utf-8"))
    raw = json.load(open(P("data", "raw", "malipages.json"), encoding="utf-8"))
    geo = {}
    if os.path.exists(P("data", "raw", "geocache.json")):
        geo = json.load(open(P("data", "raw", "geocache.json"), encoding="utf-8"))

    replaces = []
    for c in curated["entries"]:
        for pat in c.get("replaces", []):
            replaces.append((fold(pat), c))

    entries, seen_ids, seen_keys, dropped = [], set(), set(), []
    for c in curated["entries"]:
        e = dict(c); e.pop("replaces", None)
        e["source"] = dict(e.get("source", {}))
        e["source"].setdefault("verified", curated["verified"])
        entries.append(e); seen_ids.add(e["id"]); seen_keys.add(fold(e["name"]))

    for src_cat, items in raw.items():
        for it in items:
            rn = it["name"].replace("’", "'")
            if EXCLUDE.search(rn):
                dropped.append((src_cat, rn, "exclu")); continue
            quartier, address, city = split_addr(it["addr"])
            if city and fold(city) not in {"bamako", "kati", "kalabancoro", "baguineda", "niamana"}:
                dropped.append((src_cat, rn, "hors Bamako")); continue
            if not city and not it["addr"]:
                pass  # adresse inconnue mais probablement Bamako
            matched = None
            for pat, cur in replaces:
                if pat in fold(rn):
                    matched = cur; break
            phones = phones_from(it["tel"])
            if matched:
                # complète la fiche vérifiée avec les numéros Malipages absents
                have = {p["number"] if isinstance(p, dict) else p for p in matched["phones"]}
                for n in phones:
                    if n not in have:
                        matched["phones"].append({"number": n, "label": "Malipages"})
                if not matched.get("website") and it.get("web"):
                    matched["website"] = it["web"]
                dropped.append((src_cat, rn, "fusionné -> " + matched["id"])); continue
            acro, name, _ = split_name(rn)
            name = re.sub(r"^Commissariat de Police\s*—\s*(\S+)\s*Arrondissement$",
                          r"Commissariat de police du \1 arrondissement", name)
            key = fold(name)
            if key in seen_keys:          # la même structure figure dans deux catégories Malipages
                dropped.append((src_cat, rn, "doublon")); continue
            seen_keys.add(key)
            cat = categorize(rn, src_cat)
            eid = slug(acro + "-" + name if acro else name)
            k = 2
            while eid in seen_ids:
                eid = f"{slug(name)}-{k}"; k += 1
            seen_ids.add(eid)
            commune = guess_commune(it["addr"], quartier)
            if fold(city) in {"kati", "kalabancoro", "baguineda", "niamana"}:
                commune = "Kati (hors District)"
            e = {
                "id": eid, "name": name, "category": cat, "type": guess_type(rn),
                "quartier": quartier, "commune": commune, "address": address,
                "phones": phones,
                "source": {"name": "Malipages", "url": it.get("url") or f"https://www.malipages.com/annuaire/{src_cat}/",
                           "date": iso_date(it.get("date"))},
            }
            if acro: e["acronym"] = acro
            if it.get("fax"):
                fx = phones_from(it["fax"])
                if fx: e["fax"] = fx[0]
            if it.get("web"): e["website"] = it["web"]
            entries.append(e)

    # géocodage
    n_geo = 0
    for e in entries:
        g = geo.get(e["id"])
        if g and g.get("lat"):
            e["lat"], e["lng"] = round(g["lat"], 6), round(g["lng"], 6); n_geo += 1

    # nettoyage final
    for e in entries:
        e["phones"] = [p if isinstance(p, dict) else {"number": p} for p in e.get("phones", [])]
        for p in e["phones"]:
            if not p.get("label"): p.pop("label", None)
        e.pop("_hay", None)
    entries.sort(key=lambda e: (e["category"], fold(e["name"])))

    out = {
        "meta": {"generated": datetime.date.today().isoformat(), "repo": "", "contact": "",
                 "count": len(entries), "geocoded": n_geo},
        "categories": curated["categories"],
        "urgences": curated["urgences"],
        "entries": entries,
    }
    json.dump(out, open(P("data", "annuaire.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print("total", len(entries), "geocodées", n_geo)
    print(Counter(e["category"] for e in entries))
    print(Counter(e.get("commune") or "(inconnue)" for e in entries))
    with open(P("scripts", "cache", "dropped.txt"), "w", encoding="utf-8") as f:
        for d in dropped: f.write(" | ".join(d) + "\n")
    print("écartées :", len(dropped), "(voir scripts/cache/dropped.txt)")

if __name__ == "__main__":
    main()
