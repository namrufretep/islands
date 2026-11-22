"""Draft artwork renderer. Requires explicitly reviewed coastline metadata."""
import argparse, json, hashlib, random, math
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw
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
# Build a sculpted dome inside the exact coastline, blended with broad DEM relief.
h,w=z.shape
rings=path.split(' Z')
mask_img=Image.new('1',(w,h))
draw=ImageDraw.Draw(mask_img)
for idx,ring in enumerate(rings):
    if not ring.strip(): continue
    pts=[]
    for token in ring.replace('M','').replace('L','').split():
        px,py=map(float,token.split(','))
        mx=(px-1024)*mpp+(x0+x1)/2
        my=(1024-py)*mpp+(y0+y1)/2
        pts.append(((mx-t[2])/t[0]-.5,(my-t[5])/t[4]-.5))
    draw.polygon(pts,fill=1 if idx==0 else 0)
land=np.array(mask_img,dtype=bool)
dist=gaussian_filter(distance_transform_edt(land),5)
dist/=max(dist.max(),1)
relief=gaussian_filter(z,22)
relief/=max(relief[land].max(),1)
surface=gaussian_filter((1-np.exp(-dist*7))*land,5)*680+relief*190
sy,sx=np.gradient(surface,20)
palette=['#103b45','#205e68','#36969b','#78c5c1','#b5ded4','#eef5e8']
for edition,angle in [('N',0),('S',180)]:
    sign=1 if edition=='N' else -1
    normal=np.sqrt(1+sx*sx+sy*sy)
    light=(.78+sign*(.46*sx+.42*sy))/normal
    light=gaussian_filter(light,3)
    shapes=[]
    def smooth_path(coords):
        # Rounded vector joins: midpoint quadratic curves retain broad sculptural facets.
        pts=coords[:-1] if coords[0]==coords[-1] else coords
        if len(pts)<3: return ''
        mid=lambda a,b: ((a[0]+b[0])/2,(a[1]+b[1])/2)
        fmt=lambda a:f'{a[0]:.2f},{a[1]:.2f}'
        return 'M '+fmt(mid(pts[-1],pts[0]))+' '+' '.join('Q '+fmt(v)+' '+fmt(mid(v,pts[(k+1)%len(pts)])) for k,v in enumerate(pts))+' Z'
    for level,color in zip([.22,.43,.63,.80,.89],palette[1:]):
        mask=np.pad(light>level,1,constant_values=False)
        curves=[]
        for contour in find_contours(mask.astype(float),.5):
            if len(contour)<85: continue
            pts=approximate_polygon(contour,tolerance=2.1)
            if len(pts)<4: continue
            coords=[point(r-1,c-1) for r,c in pts]
            curves.append(smooth_path(coords))
        shapes.append(f'<path d="{" ".join(curves)}" fill="{color}" fill-rule="evenodd" transform="rotate({angle} 1024 1024)"/>')
    svg=f'''<svg data-art-version="3.0" xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs><radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="url(#bg)"/>
<g clip-path="url(#coast)"><rect width="2048" height="2048" fill="#103b45"/>{''.join(shapes)}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="#080b0d" stroke-width="13" stroke-linejoin="round"/>
</svg>'''
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':'Glacial Turquoise','art_status':'experimental_draft','terrain_guided':True,'art_version':'3.0','surface_model':'sculpted coastline dome blended with DEM'},indent=2))
