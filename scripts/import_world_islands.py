"""Import named islands from GeoNames, retaining stable source IDs.
Run with Python 3; source CC BY 4.0, https://www.geonames.org/.
"""
import csv, io, json, urllib.request, zipfile
from pathlib import Path
url="https://download.geonames.org/export/dump/allCountries.zip"
with urllib.request.urlopen(url,timeout=300) as response:
    archive=zipfile.ZipFile(io.BytesIO(response.read()))
rows=[]
with archive.open("allCountries.txt") as raw:
    for row in csv.reader(io.TextIOWrapper(raw,encoding="utf-8"),delimiter="\t"):
        if len(row)<19 or row[6]!="T" or row[7]!="ISL": continue
        rows.append({"sourceId":"geonames:"+row[0],"name":row[1],"countryCode":row[8],"latitude":float(row[4]),"longitude":float(row[5])})
if len(rows)<1000: raise RuntimeError("Unexpectedly small registry")
rows.sort(key=lambda r:(r["name"].casefold(),r["sourceId"]))
Path("public/data").mkdir(parents=True,exist_ok=True)
Path("public/data/world-islands.json").write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
print(len(rows),"named islands imported")
