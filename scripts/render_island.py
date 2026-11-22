"""Draft artwork renderer. Requires explicitly reviewed coastline metadata."""
import argparse, json, hashlib, random, math
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
import io
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
from skimage.measure import find_contours, approximate_polygon

p=argparse.ArgumentParser()
p.add_argument('coastline',type=Path)
p.add_argument('metadata',type=Path)
p.add_argument('output',type=Path)
a=p.parse_args()
meta=json.loads(a.metadata.read_text())
if meta.get('status')!='verified_coastline':
    raise SystemExit('Coastline must be reviewed and approved before rendering.')
raw=a.coastline.read_bytes()
if meta.get('svg_sha256')!=hashlib.sha256(raw).hexdigest():
    raise SystemExit('Coastline checksum mismatch')
path=ET.fromstring(raw).find('{http://www.w3.org/2000/svg}path').attrib['d']
from xml.sax.saxutils import quoteattr
d=quoteattr(path)
a.output.mkdir(parents=True,exist_ok=True)
terrain_dir=Path('data/gis')/meta['id']/'terrain'
tm=json.loads((terrain_dir/'terrain-00.json').read_text())
cm=json.loads(a.coastline.with_suffix('.json').read_text())
assert tm['crs']==cm['projection']
z=np.load(terrain_dir/'terrain-00.npz')['elevation'].astype(float)
valid=np.isfinite(z)
z=z[tuple(distance_transform_edt(~valid,return_distances=False,return_indices=True))]
z=gaussian_filter(z,8)
gy,gx=np.gradient(z,20)
x0,y0,x1,y1=cm['bounds_m']
mpp=cm['meters_per_pixel']
t=tm['transform']
def point(row,col):
    return (1024+(t[2]+(col+.5)*t[0]-(x0+x1)/2)/mpp,1024-(t[5]+(row+.5)*t[4]-(y0+y1)/2)/mpp)
palette=['#0c3541','#145764','#278c99','#61c8c9','#afe5df','#edf7f5']
for edition,angle in [('N',0),('S',180)]:
    sign=1 if edition=='N' else -1
    normal=np.sqrt(1+2.25*(gx*gx+gy*gy))
    light=(.65+sign*1.5*(.55*gx+.52*gy))/normal
    light=gaussian_filter(light,4)
    shapes=[]
    for level,color in zip([.12,.38,.56,.72,.84],palette[1:]):
        mask=np.pad(light>level,1,constant_values=False)
        curves=[]
        for contour in find_contours(mask.astype(float),.5):
            if len(contour)<65: continue
            pts=approximate_polygon(contour,tolerance=1.6)
            if len(pts)<4: continue
            coords=[point(r-1,c-1) for r,c in pts]
            curves.append('M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in coords)+' Z')
        shapes.append(f'<path d="{" ".join(curves)}" fill="{color}" fill-rule="evenodd" transform="rotate({angle} 1024 1024)"/>')
    svg=f'''<svg data-art-version="2.0" xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs><radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="url(#bg)"/>
<g clip-path="url(#coast)"><rect width="2048" height="2048" fill="#0c3541"/>{''.join(shapes)}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="#080b0d" stroke-width="13" stroke-linejoin="round"/>
</svg>'''
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':'Glacial Turquoise','art_status':'experimental_draft','terrain_guided':True,'art_version':'2.0'},indent=2))
