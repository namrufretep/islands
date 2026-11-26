"""Improve Samosir N water contrast using the existing geographic lake polygons."""
from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
from pyproj import Transformer
import cairosvg

root=Path('public/drafts/000056')
original=root/'freshwater-20261126/000056-N-draft.png'
meta=json.loads(original.with_suffix('.json').read_text())
geo=json.loads(Path('public/drafts/freshwater-sources-20261126/000056-samosir-water.geojson').read_text())
project=Transformer.from_crs('EPSG:4326',meta['projection'],always_xy=True).transform
x0,y0,x1,y1=meta['bounds_m'];cx=(x0+x1)/2;cy=(y0+y1)/2;mpp=meta['artwork_meters_per_pixel']
def ring(coords):
 points=[project(lon,lat) for lon,lat,*_ in coords]
 return 'M '+' L '.join(f'{1024+(x-cx)/mpp:.6f},{1024-(y-cy)/mpp:.6f}' for x,y in points)+' Z'
paths=[]
for feature in geo['features']:
 geometry=feature['geometry'];polygons=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates']
 for polygon in polygons:paths.append(' '.join(ring(coords) for coords in polygon))
water_color='#718e83'
svg='<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048">'+''.join(f'<path d="{path}" fill="{water_color}" fill-rule="evenodd"/>' for path in paths)+'</svg>'
overlay=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
before=np.array(Image.open(original).convert('RGB'))
alpha=np.array(overlay.getchannel('A'));old_color=np.array([int(meta['background'][i:i+2],16) for i in (1,3,5)])
core=alpha==255
agreement=float(np.all(before[core]==old_color,axis=1).mean())
if agreement<.98:raise RuntimeError(f'Water geometry does not align with original image: {agreement}')
after=np.array(Image.alpha_composite(Image.fromarray(before).convert('RGBA'),overlay).convert('RGB'))
assert np.array_equal(before[alpha==0],after[alpha==0])
out=root/'water-contrast-20261126';out.mkdir(exist_ok=True)
image_path=out/'000056-N-draft.png';Image.fromarray(after).save(image_path,dpi=(300,300),optimize=True)
metadata={**meta,'inland_water_color':water_color,'water_visibility_revision':'sage-water-20261126','water_geometry_unchanged':True,'artwork_sha256':hashlib.sha256(image_path.read_bytes()).hexdigest()}
image_path.with_suffix('.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'water_polygons':len(paths),'aligned_core_fraction':agreement,'changed_pixels':int(np.any(before!=after,axis=2).sum()),'unchanged_outside_water':True,'output':str(image_path)}))
