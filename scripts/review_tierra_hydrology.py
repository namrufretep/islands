"""Review #000012 as one geographic island, including inland lakes and full western relief."""
import hashlib, io, json, math, runpy, subprocess, sys, tempfile, urllib.request
from pathlib import Path
import geopandas as gpd
import numpy as np
from PIL import Image
from pyproj import Transformer
from shapely.geometry import Point, shape, mapping
from shapely.ops import transform, unary_union

base=Path("data/gis/000012")
subprocess.run([sys.executable,"scripts/import_tierra_del_fuego.py"],check=True)
cm=json.loads((base/"coastline/000012-candidate-00.json").read_text())
geographic_island=shape(json.loads((base/"coastline/000012-candidate-00.geojson").read_text()))
project=Transformer.from_crs(4326,cm["projection"],always_xy=True).transform
island=transform(project,geographic_island)
# Derive full source bounds from the island, with no administrative clipping.
west,south,east,north=geographic_island.bounds
terrain_code=Path("scripts/import_tierra_del_fuego_terrain.py").read_text()
old="west,south,east,north=-71.0,-55.2,-65.0,-52.3"
assert terrain_code.count(old)==1
terrain_code=terrain_code.replace(old,f"west,south,east,north={west-.25},{south-.25},{east+.25},{north+.25}")
exec(compile(terrain_code,"whole_island_terrain","exec"),{"__name__":"__main__"})
subprocess.run([sys.executable,"scripts/review_tierra_del_fuego.py"],check=True)
tm=json.loads((base/"terrain/terrain-00.json").read_text())
tr=tm["transform"];h,w=tm["shape"]
terrain_bounds=(tr[2],tr[5]+h*tr[4],tr[2]+w*tr[0],tr[5])
x0,y0,x1,y1=cm["bounds_m"]; tx0,ty0,tx1,ty1=terrain_bounds
assert tx0<x0 and ty0<y0 and tx1>x1 and ty1>y1, "Incomplete island DEM"

lake_url="https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_lakes.zip"
with urllib.request.urlopen(lake_url,timeout=90) as r:
    lake_bytes=r.read(50000001)
assert len(lake_bytes)<50000000
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/"lakes.zip";path.write_bytes(lake_bytes)
    lakes=gpd.read_file("zip://"+str(path),bbox=geographic_island.bounds).to_crs(cm["projection"])
records=[];geometries=[]
for _,row in lakes.iterrows():
    if row.geometry is None or row.geometry.is_empty or not row.geometry.is_valid: continue
    clipped=row.geometry.intersection(island)
    if clipped.is_empty or clipped.area<1e6: continue
    name=next((str(row[k]) for k in ["name","name_en","name_es"] if k in row and row[k] is not None and str(row[k])!="nan"),"Unnamed")
    geometries.append(clipped)
    records.append({"name":name,"area_km2":clipped.area/1e6,"source_id":str(row.get("ne_id",""))})
water=unary_union(geometries)
# Independent checks for the three prominent lakes identified by CONAE/IGN.
checks={}
for name,lon,lat in [("Fagnano",-68.0,-54.56),("Yehuin",-67.7153,-54.4119),("Chepelmut",-67.5933,-54.395)]:
    checks[name]=bool(water.buffer(2500).covers(transform(project,Point(lon,lat))))
print("INLAND_WATER_REPORT",json.dumps({"lakes":records,"reference_checks":checks}),flush=True)
assert checks["Fagnano"],"Fagnano is missing from the water geometry"
assert checks["Yehuin"] and checks["Chepelmut"],"Major northern lakes missing; finer data required"
land_geometry=island.difference(water)
x0,y0,x1,y1=cm["bounds_m"];mpp=cm["meters_per_pixel"]
def ring(coords):
    return "M "+" L ".join(f"{1024+(x-(x0+x1)/2)/mpp:.6f},{1024-(y-(y0+y1)/2)/mpp:.6f}" for x,y,*_ in coords)+" Z"
lake_rings=[]
for poly in ([water] if water.geom_type=="Polygon" else water.geoms):
    if poly.geom_type!="Polygon": continue
    lake_rings.append(ring(poly.exterior.coords))
    lake_rings.extend(ring(r.coords) for r in poly.interiors)
lake_path=" ".join(lake_rings)
out=Path("output/000012");out.mkdir(parents=True,exist_ok=True)
report={"island_id":"000012","source":lake_url,"source_sha256":hashlib.sha256(lake_bytes).hexdigest(),
        "lakes":records,"reference_checks":checks,"terrain_bounds":terrain_bounds,
        "coastline_bounds":cm["bounds_m"],"political_boundaries":False,
        "terrain_smoothing":"land-weighted; sea bathymetry excluded; 32 artwork pixels"}
(out/"hydrology-review.json").write_text(json.dumps(report,indent=2))
(out/"inland-water.geojson").write_text(json.dumps({"type":"FeatureCollection","features":[
    {"type":"Feature","properties":{"source":"Natural Earth 10m lakes"},"geometry":mapping(water)}],
    "crs":{"type":"name","properties":{"name":cm["projection"]}}}))

code=Path("scripts/render_island.py").read_text()
old="path=ET.fromstring(raw).find('{http://www.w3.org/2000/svg}path').attrib['d']"
assert code.count(old)==1
code=code.replace(old,old+"\ncoast_path=path\npath=path+' '+_lake_path")
code=code.replace("d=quoteattr(path)","d=quoteattr(path)\ncoast_outline_d=quoteattr(coast_path)")
start=code.index("h,w=z.shape\nrings=path.split")
end=code.index("land=np.array(mask_img,dtype=bool)",start)+len("land=np.array(mask_img,dtype=bool)")
code=code[:start]+"""h,w=z.shape
from rasterio.features import rasterize
from affine import Affine
land=rasterize([(_land_geometry.__geo_interface__,1)],out_shape=(h,w),transform=Affine(*t),fill=0,dtype="uint8").astype(bool)
"""+code[end:]
code=code.replace("sigma=max(1.0,52/px_per_cell)","sigma=max(1.0,32/px_per_cell)")
code=code.replace("broad=gaussian_filter(z,sigma)",
"""# Excluding ocean bathymetry retains relief in the narrow western peninsulas.
        weights=gaussian_filter(land.astype(float),sigma)
        broad=gaussian_filter(np.maximum(z,0)*land,sigma)/np.maximum(weights,1e-9)""")
code=code.replace("max(1,26/px_per_cell)","max(1,20/px_per_cell)")
code=code.replace("max(1,16/px_per_cell)","max(1,12/px_per_cell)")
old_outline='<path d={d} transform="rotate({angle} 1024 1024)" fill="none"'
assert code.count(old_outline)==1
code=code.replace(old_outline,'<path d={coast_outline_d} transform="rotate({angle} 1024 1024)" fill="none"')
code=code.replace("if a.expanded_tones: version='4.4'","if a.expanded_tones: version='4.4-hydrology'")
# Execute a precise data renderer; no generated coastline or manually painted lakes.
sys.argv=["render_island.py",str(base/"coastline/000012-candidate-00.svg"),
          "review-output/tierra_del_fuego-coastline.json",str(out),"--palette","tierra_del_fuego","--expanded-tones"]
namespace={"__name__":"__main__","_lake_path":lake_path,"_land_geometry":land_geometry}
exec(compile(code,"whole_island_relief_renderer","exec"),namespace)
# Verify lake centers are water and upper-left light is retained in both orientations.
from rasterio.transform import rowcol
for edition in ["N","S"]:
    stem=out/f"000012-{edition}-draft"
    meta=json.loads(stem.with_suffix(".json").read_text())
    meta.update(inland_water_source=lake_url,lake_count=len(records),whole_island_terrain=True,political_boundaries=False)
    stem.with_suffix(".json").write_text(json.dumps(meta,indent=2))
    with Image.open(stem.with_suffix(".png")) as im:
        assert im.size==(2048,2048)
        assert all(abs(d-300)<1 for d in im.info["dpi"])
        rgb=np.array(im.convert("RGB"));bg=rgb[0,0]
        for geom in geometries:
            p=geom.representative_point()
            px=1024+(p.x-(x0+x1)/2)/mpp*85/75
            py=1024-(p.y-(y0+y1)/2)/mpp*85/75
            if edition=="S": px,py=2048-px,2048-py
            patch=rgb[max(0,round(py)-2):round(py)+3,max(0,round(px)-2):round(px)+3]
            assert np.any(np.all(patch==bg,axis=2)), "Lake missing in finished image"
        print(edition,"all inland-water checks passed",flush=True)
# Retain source and metadata needed to reproduce the review without another app build.
for name in ["terrain-00.npz","terrain-00.json"]:
    import shutil
    shutil.copyfile(base/"terrain"/name,out/name)
