import json, math, unicodedata, collections
from pathlib import Path
rows=json.loads(Path("public/data/world-islands.json").read_text())
def norm(s):
    return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if c.isalnum())
def distance(a,b):
    p,q=map(math.radians,[a["latitude"],b["latitude"]])
    d=math.radians(b["longitude"]-a["longitude"])
    h=math.sin((p-q)/2)**2+math.cos(p)*math.cos(q)*math.sin(d/2)**2
    return 12742*math.asin(min(1,math.sqrt(h)))
ids=collections.Counter(r["sourceId"] for r in rows)
groups=collections.defaultdict(list)
coords=collections.defaultdict(list)
for r in rows:
    groups[(r["countryCode"],norm(r["name"]))].append(r)
    coords[(r["latitude"],r["longitude"])].append(r)
near=[]
for group in groups.values():
    for i,a in enumerate(group):
        for b in group[i+1:]:
            km=distance(a,b)
            if km<=2: near.append({"a":a,"b":b,"distanceKm":round(km,4)})
exact=[g for g in coords.values() if len(g)>1]
report={"records":len(rows),"duplicateSourceIds":[k for k,v in ids.items() if v>1],"sameNameCountryGroups":sum(len(g)>1 for g in groups.values()),"nearSameNamePairs":len(near),"identicalCoordinateGroups":len(exact),"nearCandidates":near,"coordinateCandidates":exact}
Path("docs/world-island-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ("nearCandidates","coordinateCandidates")}))
