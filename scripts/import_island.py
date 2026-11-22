import argparse, hashlib, json, math, tempfile, urllib.request, zipfile
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point, mapping
from shapely.ops import unary_union
from pyproj import Geod

p=argparse.ArgumentParser()
p.add_argument('--url', required=True)
p.add_argument('--lat', type=float, required=True)
p.add_argument('--lon', type=float, required=True)
p.add_argument('--id', required=True)
p.add_argument('--output', required=True)
a=p.parse_args()
out=Path(a.output)
out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    archive=Path(tmp)/'source.zip'
    with urllib.request.urlopen(a.url,timeout=90) as response:
        data=response.read(100_000_001)
    if len(data)>100_000_000: raise ValueError('Archive too large')
    archive.write_bytes(data)
    candidates=[]
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            target=(Path(tmp)/name).resolve()
            if not target.is_relative_to(Path(tmp).resolve()): raise ValueError('Unsafe archive path')
        z.extractall(tmp)
    point=Point(a.lon,a.lat)
    for shp in Path(tmp).rglob('*.shp'):
        g=gpd.read_file(shp)
        if not g.crs: continue
        g=g.to_crs(4326)
        for geom in g.geometry:
            if geom is None or not geom.is_valid: continue
            parts=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
            for part in parts:
                if part.geom_type=='Polygon' and part.covers(point):
                    area=abs(Geod(ellps='WGS84').geometry_area_perimeter(part)[0])
                    candidates.append((area,shp.name,part))
    if not candidates: raise RuntimeError('No valid polygon contains island reference point; inspect source layers')
    # Do not automatically promote ambiguous thematic layers to verified coastlines.
    candidates.sort(key=lambda x:x[0],reverse=True)
    for i,(area,layer,geom) in enumerate(candidates):
        crs=f'+proj=aeqd +lat_0={a.lat} +lon_0={a.lon} +datum=WGS84 +units=m +no_defs'
        projected=gpd.GeoSeries([geom],crs=4326).to_crs(crs).iloc[0]
        x0,y0,x1,y1=projected.bounds
        extent=max(x1-x0,y1-y0)
        if extent<=0: raise ValueError('Invalid extent')
        scale=1536/extent
        def ring(coords):
            return 'M '+' L '.join(f'{1024+(x-(x0+x1)/2)*scale:.6f},{1024-(y-(y0+y1)/2)*scale:.6f}' for x,y,*_ in coords)+' Z'
        path=' '.join([ring(projected.exterior.coords)]+[ring(r.coords) for r in projected.interiors])
        stem=f'{a.id}-candidate-{i:02}'
        (out/(stem+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048" width="2048" height="2048"><path d="{path}" fill="#61c8c9" fill-rule="evenodd"/></svg>')
        (out/(stem+'.geojson')).write_text(json.dumps(mapping(geom)))
        (out/(stem+'.json')).write_text(json.dumps(dict(id=a.id,status='unverified_candidate',source=a.url,source_sha256=hashlib.sha256(data).hexdigest(),layer=layer,area_km2=area/1e6,projection=crs,bounds_m=[x0,y0,x1,y1],meters_per_pixel=1/scale,print_scale_denominator=(1/scale)*300/0.0254,canvas_px=2048,island_extent_px=1536,dpi_target=300),indent=2))
    print(f'Exported {len(candidates)} unverified coastline candidates; human layer verification required.')
