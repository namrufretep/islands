import json,hashlib
from pathlib import Path
from shapely.geometry import shape,Point
from pyproj import Geod
import numpy as np
base=Path("data/gis/000008")
stem=base/"coastline/000008-candidate-00"
m=json.loads(stem.with_suffix(".json").read_text())
g=shape(json.loads(stem.with_suffix(".geojson").read_text()))
area=abs(Geod(ellps="WGS84").geometry_area_perimeter(g)[0])/1e6
assert g.is_valid and g.covers(Point(-73.97,40.78)) and 50<area<70,area
t=json.loads((base/"terrain/terrain-00.json").read_text())
assert t["crs"]==m["projection"]
with np.load(base/"terrain/terrain-00.npz") as raster:
    assert list(raster["elevation"].shape)==t["shape"]
    assert np.nanmax(raster["elevation"])>40
m.update(status="verified_coastline",svg_sha256=hashlib.sha256(stem.with_suffix(".svg").read_bytes()).hexdigest(),verification="Automated source geometry, area and reference-point checks; human visual review pending",attribution="OpenStreetMap coastline (ODbL), Mapzen/AWS terrain; confirm data licensing before NFT release")
Path("review-output").mkdir(exist_ok=True)
Path("review-output/manhattan-coastline.json").write_text(json.dumps(m,indent=2))
