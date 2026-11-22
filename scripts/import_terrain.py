import argparse, tempfile, urllib.request, zipfile, json, hashlib
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

p=argparse.ArgumentParser()
p.add_argument('--url',required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--lat',type=float,required=True)
p.add_argument('--lon',type=float,required=True)
a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    with urllib.request.urlopen(a.url,timeout=90) as r: data=r.read(100000001)
    if len(data)>100000000: raise ValueError('Archive too large')
    archive=root/'source.zip'; archive.write_bytes(data)
    with zipfile.ZipFile(archive) as z:
        if sum(i.file_size for i in z.infolist())>500000000: raise ValueError('Expanded archive too large')
        for n in z.namelist():
            if not (root/n).resolve().is_relative_to(root.resolve()): raise ValueError('Unsafe archive')
        z.extractall(root)
    candidates=[f for f in root.rglob('*') if f.suffix.lower() in ('.tif','.tiff','.asc','.dem','.bil','.img')]
    if not candidates: raise RuntimeError('No supported raster found; inspect archive format')
    crs=f'+proj=aeqd +lat_0={a.lat} +lon_0={a.lon} +datum=WGS84 +units=m +no_defs'
    count=0
    for f in candidates:
        with rasterio.open(f) as src:
            if not src.crs: continue
            transform,w,h=calculate_default_transform(src.crs,crs,src.width,src.height,*src.bounds,resolution=20)
            if w*h>25000000: raise ValueError('Unexpected raster extent')
            elevation=np.full((h,w),np.nan,dtype='float32')
            reproject(source=rasterio.band(src,1),destination=elevation,src_transform=src.transform,src_crs=src.crs,src_nodata=src.nodata,dst_transform=transform,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear)
            if not np.isfinite(elevation).any(): continue
            gy,gx=np.gradient(elevation,20)
            slope=np.degrees(np.arctan(np.hypot(gx,gy)))
            stem=a.output/f'terrain-{count:02}'
            np.savez_compressed(stem.with_suffix('.npz'),elevation=elevation,slope=slope,east_gradient=gx,north_gradient=-gy)
            stem.with_suffix('.json').write_text(json.dumps(dict(status='unverified_terrain',source=a.url,source_sha256=hashlib.sha256(data).hexdigest(),layer=f.name,crs=crs,transform=list(transform)[:6],shape=[h,w],min_m=float(np.nanmin(elevation)),max_m=float(np.nanmax(elevation)),resolution_m=20),indent=2))
            count+=1
    if not count: raise RuntimeError('No georeferenced elevation raster exported')
