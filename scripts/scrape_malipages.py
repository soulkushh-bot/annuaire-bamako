"""Récupère les fiches des catégories utiles de l'annuaire Malipages (nom, adresse, tél., fax, site, date, URL de la fiche).
Usage : python scripts/scrape_malipages.py data/raw/malipages.json
"""
import re, html, json, subprocess, sys, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
CATS = ["ministeres", "mairies", "cliniques-et-hopitaux", "ecoles-et-universites", "gouvernement-ambassades",
        "services-medicaux", "telecom", "presse"]

def fetch(url):
    r = subprocess.run(["curl", "-sL", "-A", UA, "-H", "Accept-Language: fr", "--max-time", "40", "-w", "\n%{http_code}", url],
                       capture_output=True)
    body, code = r.stdout.decode("utf-8", "ignore").rsplit("\n", 1)
    return code.strip(), body

def parse(body):
    hrefs = []
    for h in re.findall(r'href="(https://www\.malipages\.com/annuaire/lien/[^"]+)"', body):
        if h not in hrefs:
            hrefs.append(h)
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", s))
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    ents, i = [], 0
    while i < len(lines):
        if lines[i] == "Adresse :" and i >= 2 and lines[i - 1] == lines[i - 2]:
            e = {"name": lines[i - 1], "addr": [], "tel": "", "fax": "", "web": "", "date": "", "url": ""}
            j = i + 1
            while j < len(lines) and lines[j] != "Plus" and j < i + 25:
                l = lines[j]
                if l.startswith("Tél."): e["tel"] = l.split(":", 1)[1].strip()
                elif l.startswith("Fax."): e["fax"] = l.split(":", 1)[1].strip()
                elif l == "Site web :": e["web"] = lines[j + 1] if j + 1 < len(lines) else ""; j += 1
                elif re.match(r"\d\d/\d\d/\d{4}$", l): e["date"] = l
                elif not e["tel"] and not e["date"]: e["addr"].append(l)
                j += 1
            e["addr"] = " ".join(e["addr"]).strip(" -")
            ents.append(e); i = j
        else:
            i += 1
    if len(hrefs) == len(ents):
        for e, h in zip(ents, hrefs): e["url"] = h
    return ents

def main(out):
    res = {}
    for c in CATS:
        allents = []
        for p in range(1, 60):
            url = f"https://www.malipages.com/annuaire/{c}/" + (f"page/{p}/" if p > 1 else "")
            code, body = fetch(url)
            if code != "200": break
            ents = parse(body)
            if not ents: break
            allents += ents
            print(c, "page", p, len(ents), "urls:", sum(1 for e in ents if e["url"]), flush=True)
            time.sleep(0.5)
        res[c] = allents
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: len(v) for k, v in res.items()})

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/malipages.json")
