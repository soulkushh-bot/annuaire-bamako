"""Géocode les fiches via Nominatim (OpenStreetMap), avec cache et règles strictes :
seuls les résultats situés dans l'agglomération de Bamako ET dont le nom recoupe celui de la fiche sont retenus.
Un point approximatif au niveau du quartier n'est jamais accepté (il fausserait l'itinéraire).

Usage : python scripts/build_data.py && python scripts/geocode.py && python scripts/build_data.py
Respecte la politique Nominatim : 1 requête/seconde, User-Agent identifié.
"""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
CACHE = P("data", "raw", "geocache.json")
UA = "annuaire-bamako/1.0 (projet open data ; contact via le dépôt GitHub)"
BBOX = (12.45, 12.80, -8.20, -7.80)  # lat min, lat max, lon min, lon max (Bamako + Kati)
STOP = {"de", "du", "des", "la", "le", "les", "et", "d", "l", "au", "aux", "a", "en", "pour", "mali", "bamako", "national",
        "nationale", "direction", "generale", "general", "agence", "office", "centre", "ministere", "societe", "institut",
        "ecole", "clinique", "hopital", "cabinet", "sa", "sarl", "ex", "commune", "du", "district"}

def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()

def tokens(s, keep_generic=False):
    return {t for t in re.findall(r"[a-z0-9]+", fold(s)) if len(t) > 2 and (keep_generic or t not in STOP)}

def variants(e):
    """Formes de requête à essayer : OSM nomme « Hôpital Gabriel Touré », jamais « CHU Gabriel Touré »."""
    base = re.sub(r"\(.*?\)|—.*$", "", e["name"])
    base = re.sub(r"[«»\"']", " ", base)
    base = re.sub(r"\s+", " ", base).strip(" ,-")
    # (requête, strict) : « strict » marque une requête bâtie sur une partie du nom seulement,
    # que l'on revalide ensuite contre le nom complet.
    out = [(base, False)]
    m = re.match(r"^CHU[\s-]+(?:du |de la |de |d')?(.+)$", base, re.I)
    if m:
        out.append(("Hôpital " + m.group(1), False))
    if re.match(r"^Hôpital\b", base, re.I):
        out.append(("CHU " + re.sub(r"^Hôpital\s+(?:du |de la |de |d')?", "", base, flags=re.I), False))
    if e.get("acronym"):
        out.append((e["acronym"], True))
    # queue distinctive : « Centre Hospitalier Mère-Enfant Le Luxembourg » -> « Le Luxembourg »
    words = base.split()
    if len(words) > 3:
        out.append((" ".join(words[-2:]), True))
    if e.get("quartier"):
        out.append((f"{base}, {e['quartier']}", False))
    seen, uniq = set(), []
    for v, strict in out:
        k = fold(v)
        if k and k not in seen:
            seen.add(k); uniq.append((v, strict))
    return uniq

def query(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": q, "format": "jsonv2", "limit": 5, "countrycodes": "ml", "namedetails": 1, "addressdetails": 1})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# Nature de l'établissement : un ministère n'est pas une agence, un institut n'est pas un ministère.
KINDS = ["ministere", "ambassade", "consulat", "mairie", "primature", "presidence", "hopital", "polyclinique", "clinique",
         "universite", "faculte", "lycee", "ecole", "institut", "academie", "direction", "agence", "office", "commissariat",
         "tribunal", "cour", "laboratoire", "musee", "bibliotheque", "caisse", "chambre", "conseil", "commission",
         "autorite", "bureau", "centre", "stade", "aeroport", "gare"]

def kind_of(s):
    t = tokens(s, keep_generic=True)
    return next((k for k in KINDS if k in t), None)

def acronym_ok(acro, res):
    """Le sigle doit ouvrir le nom du lieu ou y figurer entre parenthèses — pas apparaître n'importe où
    (« Sougou dni » n'est pas la Direction Nationale de l'Industrie)."""
    nd = res.get("namedetails") or {}
    name = fold(nd.get("name") or nd.get("name:fr") or "")
    toks = re.findall(r"[a-z0-9]+", name)
    a = fold(acro)
    return bool(toks) and (toks[0] == a or name == a or a in re.findall(r"\(([^)]*)\)", name))

def accept(e, res, strict=False):
    lat, lon = float(res["lat"]), float(res["lon"])
    if not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lon <= BBOX[3]):
        return False
    if res.get("class") in {"place", "highway", "boundary", "landuse", "natural", "waterway", "public_transport", "railway"}:
        return False
    # Un arrêt de bus porte souvent le nom de l'établissement voisin : ce n'est pas l'établissement.
    if re.match(r"arret|arrêt|station\b", fold(res.get("display_name", ""))):
        return False
    names = " ".join(str(v) for v in (res.get("namedetails") or {}).values()) + " " + res.get("display_name", "")

    # Nature contradictoire : « Institut National de la Jeunesse et des Sports » n'est pas le ministère.
    mine, theirs = kind_of(e["name"]), kind_of(names)
    if mine and theirs and mine != theirs and mine not in tokens(names, keep_generic=True):
        return False

    if e.get("acronym") and acronym_ok(e["acronym"], res):
        return True
    want = tokens(e["name"]) | tokens(e.get("acronym", ""))
    need = 1 if len(want) <= 1 else 2
    if not want:
        # Nom entièrement composé de mots génériques (« Hôpital du Mali ») : on les réutilise,
        # mais en exigeant qu'ils correspondent presque tous.
        want = tokens(e["name"], keep_generic=True)
        need = max(2, len(want) - 1)
    elif strict:
        # Requête bâtie sur une partie du nom seulement : on exige que le résultat recoupe
        # l'essentiel du nom complet, sinon « … et des Sports » attrape n'importe quoi.
        need = max(2, -(-len(want) * 7 // 10))
    got = tokens(names, keep_generic=True)
    return len(want & got) >= need

def main():
    data = json.load(open(P("data", "annuaire.json"), encoding="utf-8"))
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    args = sys.argv[1:]
    retry = "--retry" in args            # relance les fiches restées sans coordonnées
    only = {a for a in args if not a.startswith("--")}
    def pending(e):
        if only:
            return e["id"] in only
        c = cache.get(e["id"])
        return c is None or (retry and not c.get("lat"))
    todo = [e for e in data["entries"] if pending(e)]
    print(len(todo), "fiches à géocoder")
    for i, e in enumerate(todo, 1):
        if e["category"] == "urgences":
            cache[e["id"]] = {"lat": None, "q": None}; continue
        cands = [(f"{v}, Bamako", strict) for v, strict in variants(e)]
        hit = None
        for q, strict in cands:
            try:
                for res in query(q):
                    if accept(e, res, strict):
                        hit = {"lat": float(res["lat"]), "lng": float(res["lon"]), "q": q,
                               "osm": f"{res.get('osm_type')}/{res.get('osm_id')}", "label": res.get("display_name", "")[:120]}
                        break
            except Exception as ex:  # réseau, quota…
                print("  !", q, ex)
            time.sleep(1.1)
            if hit:
                break
        cache[e["id"]] = hit or {"lat": None, "q": cands[0][0]}
        print(f"[{i}/{len(todo)}]", "OK " if hit else "-- ", e["name"][:60], (hit or {}).get("label", "")[:70], flush=True)
        if i % 10 == 0:
            json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("géocodées :", sum(1 for v in cache.values() if v and v.get("lat")), "/", len(cache))

if __name__ == "__main__":
    main()
