import hashlib,json,urllib.request,urllib.parse
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point,Polygon,mapping
from pyproj import Geod
out=Path("data/gis/000007/coastline")
out.mkdir(parents=True,exist_ok=True)
import xml.etree.ElementTree as ET
from shapely.ops import polygonize,unary_union
from shapely.geometry import LineString
url="https://api.openstreetmap.org/api/0.6/map?bbox=9.183,47.697,9.209,47.714"
req=urllib.request.Request(url,headers={"User-Agent":"ISLANDS geographic artwork research"})
with urllib.request.urlopen(req,timeout=90) as response: archive=response.read(30000000)
root=ET.fromstring(archive)
nodes={n.attrib["id"]:(float(n.attrib["lon"]),float(n.attrib["lat"])) for n in root.findall("node")}
inner={m.attrib["ref"] for rel in root.findall("relation") for m in rel.findall("member") if m.attrib.get("role")=="inner" and m.attrib.get("type")=="way"}
lines=[]
for w in root.findall("way"):
    tags={t.attrib["k"]:t.attrib["v"] for t in w.findall("tag")}
    if w.attrib["id"] in inner or tags.get("natural") in ("water","coastline") or tags.get("place")=="island" or tags.get("waterway")=="riverbank":
        pts=[nodes.get(n.attrib["ref"]) for n in w.findall("nd")]
        if len(pts)>1 and all(p is not None for p in pts): lines.append(LineString(pts))
candidates=[p for p in polygonize(unary_union(lines)) if p.covers(Point(9.195,47.705)) and 0.3<abs(Geod(ellps="WGS84").geometry_area_perimeter(p)[0])/1e6<0.7]
if len(candidates)!=1: raise ValueError("Mainau island boundary not uniquely verified")
island=candidates[0]
crs="+proj=aeqd +lat_0=47.705 +lon_0=9.195 +datum=WGS84 +units=m +no_defs"
projected=gpd.GeoSeries([island],crs=4326).to_crs(crs).iloc[0]
x0,y0,x1,y1=projected.bounds
scale=1536/max(x1-x0,y1-y0)
def ring(coords):
    return "M "+" L ".join(f"{1024+(x-(x0+x1)/2)*scale:.6f},{1024-(y-(y0+y1)/2)*scale:.6f}" for x,y,*_ in coords)+" Z"
d=" ".join([ring(projected.exterior.coords)]+[ring(interior.coords) for interior in projected.interiors])
stem=out/"000007-candidate-00"
stem.with_suffix(".svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" width="2048" height="2048"><path d="{d}" fill="#b8a08a" fill-rule="evenodd"/></svg>')
stem.with_suffix(".geojson").write_text(json.dumps(mapping(island)))
area=abs(Geod(ellps="WGS84").geometry_area_perimeter(island)[0])/1e6
stem.with_suffix(".json").write_text(json.dumps(dict(id="000007",name="Mainau",status="unverified_candidate",source=url,source_sha256=hashlib.sha256(archive).hexdigest(),layer="OSM map API water boundaries and island polygons",area_km2=area,projection=crs,bounds_m=[x0,y0,x1,y1],meters_per_pixel=1/scale,canvas_px=2048,island_extent_px=1536,dpi_target=300,attribution="OpenStreetMap contributors, ODbL; licensing review required"),indent=2))
print(f"Mainau coastline candidate imported: {area:.1f} km²")
