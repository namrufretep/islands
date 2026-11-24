import hashlib,json,urllib.request,urllib.parse
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point,Polygon,mapping
from pyproj import Geod
out=Path("data/gis/000008/coastline")
out.mkdir(parents=True,exist_ok=True)
import xml.etree.ElementTree as ET
from shapely.ops import polygonize,unary_union
from shapely.geometry import LineString
# Download shoreline-only OSM-derived land polygons, avoiding dense urban map objects.
import tempfile
url="https://osmdata.openstreetmap.de/download/land-polygons-split-4326.zip"
# Prefer a small regional Natural Earth candidate if it passes strict island checks;
# otherwise use OSM coastline data via a focused Overpass query.
url="https://overpass-api.de/api/interpreter"
query='[out:json][timeout:120];way["natural"="coastline"](40.69,-74.03,40.89,-73.90);out geom;'
for endpoint in ("https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter","https://overpass.private.coffee/api/interpreter"):
    try:
        req=urllib.request.Request(endpoint+"?"+urllib.parse.urlencode({"data":query}),headers={"User-Agent":"ISLANDS geographic artwork research"})
        with urllib.request.urlopen(req,timeout=150) as response: archive=response.read(30000000)
        elements=json.loads(archive)["elements"]
        lines=[LineString([(p["lon"],p["lat"]) for p in e["geometry"]]) for e in elements if len(e.get("geometry",[]))>1]
        url=endpoint
        break
    except Exception as exc: print(endpoint,exc)
else:
    raise RuntimeError("OSM coastline endpoints unavailable")
candidates=[p for p in polygonize(unary_union(lines)) if p.covers(Point(-73.97,40.78)) and 50<abs(Geod(ellps="WGS84").geometry_area_perimeter(p)[0])/1e6<70]
if len(candidates)!=1: raise ValueError("Manhattan island boundary not uniquely verified")
# Preserve external shoreline; internal cutouts require independent verification.
island=Polygon(candidates[0].exterior)
assert island.is_valid
assert 50<abs(Geod(ellps="WGS84").geometry_area_perimeter(island)[0])/1e6<70
crs="+proj=aeqd +lat_0=40.78 +lon_0=-73.97 +datum=WGS84 +units=m +no_defs"
projected=gpd.GeoSeries([island],crs=4326).to_crs(crs).iloc[0]
x0,y0,x1,y1=projected.bounds
scale=1536/max(x1-x0,y1-y0)
def ring(coords):
    return "M "+" L ".join(f"{1024+(x-(x0+x1)/2)*scale:.6f},{1024-(y-(y0+y1)/2)*scale:.6f}" for x,y,*_ in coords)+" Z"
d=" ".join([ring(projected.exterior.coords)]+[ring(interior.coords) for interior in projected.interiors])
stem=out/"000008-candidate-00"
stem.with_suffix(".svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" width="2048" height="2048"><path d="{d}" fill="#b8a08a" fill-rule="evenodd"/></svg>')
stem.with_suffix(".geojson").write_text(json.dumps(mapping(island)))
area=abs(Geod(ellps="WGS84").geometry_area_perimeter(island)[0])/1e6
stem.with_suffix(".json").write_text(json.dumps(dict(id="000008",name="Manhattan",status="unverified_candidate",source=url,source_sha256=hashlib.sha256(archive).hexdigest(),layer="OSM coastline ways",area_km2=area,projection=crs,bounds_m=[x0,y0,x1,y1],meters_per_pixel=1/scale,canvas_px=2048,island_extent_px=1536,dpi_target=300,attribution="OpenStreetMap contributors, ODbL; licensing review required"),indent=2))
print(f"Manhattan coastline candidate imported: {area:.1f} km²")
