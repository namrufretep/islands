import hashlib,json,urllib.request,urllib.parse
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point,Polygon,mapping
from pyproj import Geod
out=Path("data/gis/000007/coastline")
out.mkdir(parents=True,exist_ok=True)
url="https://overpass-api.de/api/interpreter"
query='[out:json][timeout:90];(way["place"="island"]["name"="Mainau"](47.69,9.17,47.72,9.22);relation["place"="island"]["name"="Mainau"](47.69,9.17,47.72,9.22);way["natural"="coastline"](47.69,9.17,47.72,9.22););out geom;'
req=urllib.request.Request(url,data=urllib.parse.urlencode({"data":query}).encode(),headers={"User-Agent":"ISLANDS geographic artwork research"})
for endpoint in ("https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter","https://overpass.private.coffee/api/interpreter"):
    try:
        req=urllib.request.Request(endpoint+"?"+urllib.parse.urlencode({"data":query}),headers={"User-Agent":"ISLANDS geographic artwork research"})
        with urllib.request.urlopen(req,timeout=90) as response: archive=response.read(10000000)
        json.loads(archive)
        url=endpoint
        break
    except Exception as exc:
        print(endpoint,exc)
else:
    raise RuntimeError("All OSM endpoints unavailable")
from shapely.ops import polygonize,unary_union
from shapely.geometry import LineString
lines=[]
for e in json.loads(archive)["elements"]:
    for part in ([e] if e["type"]=="way" else e.get("members",[])):
        if part.get("geometry") and part.get("role","outer") in ("outer",""):
            lines.append(LineString([(p["lon"],p["lat"]) for p in part["geometry"]]))
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
stem.with_suffix(".json").write_text(json.dumps(dict(id="000007",name="Mainau",status="unverified_candidate",source=url,source_sha256=hashlib.sha256(archive).hexdigest(),layer="OSM natural=coastline or place=island",area_km2=area,projection=crs,bounds_m=[x0,y0,x1,y1],meters_per_pixel=1/scale,canvas_px=2048,island_extent_px=1536,dpi_target=300,attribution="OpenStreetMap contributors, ODbL; licensing review required"),indent=2))
print(f"Mainau coastline candidate imported: {area:.1f} km²")
