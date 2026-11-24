"""Import Sulawesi's geographic coastline from Natural Earth 10m admin-0 land polygons.
Candidate only: never mark reviewed without human coastline/terrain inspection.
"""
import hashlib, json, urllib.request
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point, mapping
from pyproj import Geod

url="https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip"
out=Path("data/gis/000010/coastline")
out.mkdir(parents=True,exist_ok=True)
with urllib.request.urlopen(url,timeout=120) as response:
    archive=response.read(60_000_001)
if len(archive)>60_000_000: raise ValueError("Natural Earth archive exceeds size limit")
import tempfile, zipfile
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/"land.zip"
    path.write_bytes(archive)
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist())>250_000_000: raise ValueError("Archive expansion limit")
        for item in z.infolist():
            if not (Path(tmp)/item.filename).resolve().is_relative_to(Path(tmp).resolve()): raise ValueError("Unsafe archive path")
        z.extractall(tmp)
    shp=next(Path(tmp).rglob("ne_10m_land.shp"))
    geo=gpd.read_file(shp).to_crs(4326)
    ref=Point(120.0,-2.0)
    polygons=[]
    for geom in geo.geometry:
        if geom is None: continue
        parts=list(geom.geoms) if geom.geom_type=="MultiPolygon" else [geom]
        polygons.extend(p for p in parts if p.geom_type=="Polygon" and p.covers(ref))
    if len(polygons)!=1: raise RuntimeError(f"Expected one Sulawesi land polygon; found {len(polygons)}")
    island=polygons[0]
crs="+proj=aeqd +lat_0=-2.0 +lon_0=120.0 +datum=WGS84 +units=m +no_defs"
projected=gpd.GeoSeries([island],crs=4326).to_crs(crs).iloc[0]
x0,y0,x1,y1=projected.bounds
scale=1536/max(x1-x0,y1-y0)
def ring(coords):
    return "M "+" L ".join(f"{1024+(x-(x0+x1)/2)*scale:.6f},{1024-(y-(y0+y1)/2)*scale:.6f}" for x,y,*_ in coords)+" Z"
d=" ".join([ring(projected.exterior.coords)]+[ring(interior.coords) for interior in projected.interiors])
stem=out/"000010-candidate-00"
stem.with_suffix(".svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" width="2048" height="2048"><path d="{d}" fill="#b8a08a" fill-rule="evenodd"/></svg>')
stem.with_suffix(".geojson").write_text(json.dumps(mapping(island)))
area=abs(Geod(ellps="WGS84").geometry_area_perimeter(island)[0])/1e6
stem.with_suffix(".json").write_text(json.dumps(dict(id="000010",name="Sulawesi",status="unverified_candidate",source=url,source_sha256=hashlib.sha256(archive).hexdigest(),layer="ne_10m_land",area_km2=area,projection=crs,bounds_m=[x0,y0,x1,y1],meters_per_pixel=1/scale,canvas_px=2048,island_extent_px=1536,dpi_target=300,attribution="Natural Earth public domain; coastline candidate pending visual review"),indent=2))
print(f"Sulawesi coastline candidate imported: {area:.1f} km²")
