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

def tokens(s):
    return {t for t in re.findall(r"[a-z0-9]+", fold(s)) if len(t) > 2 and t not in STOP}

def query(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": q, "format": "jsonv2", "limit": 5, "countrycodes": "ml", "namedetails": 1, "addressdetails": 1})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def accept(e, res):
    lat, lon = float(res["lat"]), float(res["lon"])
    if not (BBOX[0] <= lat <= BBOX[1] and BBOX[2] <= lon <= BBOX[3]):
        return False
    if res.get("class") in {"place", "highway", "boundary", "landuse", "natural", "waterway"}:
        return False
    names = " ".join(str(v) for v in (res.get("namedetails") or {}).values()) + " " + res.get("display_name", "")
    want = tokens(e["name"]) | tokens(e.get("acronym", ""))
    got = tokens(names)
    common = want & got
    # acronyme exact ou au moins 2 mots significatifs (1 si le nom n'en a qu'un)
    if e.get("acronym") and fold(e["acronym"]) in got:
        return True
    need = 1 if len(want) <= 1 else 2
    return len(common) >= need

def main():
    data = json.load(open(P("data", "annuaire.json"), encoding="utf-8"))
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    only = set(sys.argv[1:])  # ids optionnels à (re)géocoder
    todo = [e for e in data["entries"] if (e["id"] in only) or (not only and e["id"] not in cache)]
    print(len(todo), "fiches à géocoder")
    for i, e in enumerate(todo, 1):
        if e["category"] == "urgences":
            cache[e["id"]] = {"lat": None, "q": None}; continue
        base = re.sub(r"\(.*?\)|—.*$", "", e["name"]).strip()
        cands = [f"{base}, Bamako"]
        if e.get("acronym"):
            cands.append(f"{e['acronym']}, Bamako")
        if e.get("quartier"):
            cands.append(f"{base}, {e['quartier']}, Bamako")
        hit = None
        for q in cands:
            try:
                for res in query(q):
                    if accept(e, res):
                        hit = {"lat": float(res["lat"]), "lng": float(res["lon"]), "q": q,
                               "osm": f"{res.get('osm_type')}/{res.get('osm_id')}", "label": res.get("display_name", "")[:120]}
                        break
            except Exception as ex:  # réseau, quota…
                print("  !", q, ex)
            time.sleep(1.1)
            if hit:
                break
        cache[e["id"]] = hit or {"lat": None, "q": cands[0]}
        print(f"[{i}/{len(todo)}]", "OK " if hit else "-- ", e["name"][:60], (hit or {}).get("label", "")[:70], flush=True)
        if i % 10 == 0:
            json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("géocodées :", sum(1 for v in cache.values() if v and v.get("lat")), "/", len(cache))

if __name__ == "__main__":
    main()
