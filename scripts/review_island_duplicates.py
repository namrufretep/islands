import json, collections, unicodedata
from pathlib import Path
audit=json.loads(Path("docs/world-island-audit.json").read_text())
def norm(s):
    return "".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if c.isalnum())
same=[]; aliases=[]; conflicts=[]
for group in audit["coordinateCandidates"]:
    keys={(r["countryCode"],norm(r["name"])) for r in group}
    if len(keys)==1: same.append(group)
    elif len({r["countryCode"] for r in group})==1: aliases.append(group)
    else: conflicts.append(group)
report={"sameNameSameCoordinates":same,"possibleAliases":aliases,"crossCountryConflicts":conflicts,"nearNamePairs":audit["nearCandidates"],"policy":"Review candidates against island polygons before merging. Preserve every source ID. Never merge on name alone."}
Path("docs/island-duplicate-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:len(v) for k,v in report.items() if isinstance(v,list)}))
