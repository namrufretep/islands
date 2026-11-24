"""Fetch public Mapzen/AWS elevation GeoTIFF tiles covering Grande Terre, reproject to AEQD.
Terrain remains an experimental source pending geographic and licensing review.
"""
import json, math, urllib.request, tempfile
from pathlib import Path
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform,reproject,Resampling,transform_bounds
from rasterio.transform import array_bounds

out=Path("data/gis/000009/terrain")
out.mkdir(parents=True,exist_ok=True)
# Grande Terre geographic extent with a safety margin.
west,south,east,north=163.8,-22.5,167.2,-19.9
zoom=9
def tile(lon,lat):
    lat=math.radians(lat)
    return int((lon+180)/360*(2**zoom)),int((1-math.asinh(math.tan(lat))/math.pi)/2*(2**zoom))
x0,y0=tile(west,north)
x1,y1=tile(east,south)
with tempfile.TemporaryDirectory() as tmp:
    datasets=[]
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            url=f"https://s3.amazonaws.com/elevation-tiles-prod/geotiff/{zoom}/{x}/{y}.tif"
            file=Path(tmp)/f"{x}-{y}.tif"
            with urllib.request.urlopen(url,timeout=90) as response: file.write_bytes(response.read(15_000_001))
            datasets.append(rasterio.open(file))
    mosaic,transform=merge(datasets,nodata=np.nan,dtype='float32')
    src_crs=datasets[0].crs
    # Tile grid covers much more than Grande Terre: clip output to requested bounds.
    bounds=transform_bounds('EPSG:4326',src_crs,west,south,east,north,densify_pts=21)
    crs="+proj=aeqd +lat_0=-21.3 +lon_0=165.3 +datum=WGS84 +units=m +no_defs"
    # 180m terrain resolution keeps rendering practical while retaining Grande Terre highlands's mass.
    dest_transform,w,h=calculate_default_transform(src_crs,crs,mosaic.shape[2],mosaic.shape[1],*bounds,resolution=260)
    print(f"Clipped Grande Terre DEM dimensions: {w} x {h} ({w*h:,} pixels)")
    if w*h>6000000: raise ValueError(f"Unexpected terrain extent: {w} x {h}")
    elevation=np.full((h,w),np.nan,dtype="float32")
    reproject(source=mosaic[0],destination=elevation,src_transform=transform,src_crs=src_crs,src_nodata=np.nan,dst_transform=dest_transform,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear)
    for ds in datasets: ds.close()
    if not np.isfinite(elevation).any() or np.nanmax(elevation)<1300: raise ValueError("Grande Terre highlands elevation not captured")
    np.savez_compressed(out/"terrain-00.npz",elevation=elevation)
    (out/"terrain-00.json").write_text(json.dumps(dict(status="unverified_terrain",source="Mapzen terrain tiles / AWS elevation-tiles-prod",attribution="Mapzen terrain data (sources vary); review original source licenses before release",crs=crs,transform=list(dest_transform)[:6],shape=[h,w],min_m=float(np.nanmin(elevation)),max_m=float(np.nanmax(elevation)),resolution_m=260),indent=2))
    print("Grande Terre terrain:",h,w,"max",float(np.nanmax(elevation)))
