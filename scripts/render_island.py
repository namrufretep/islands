"""Draft artwork renderer. Requires explicitly reviewed coastline metadata."""
import argparse, json, hashlib, random, math
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw
import io
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt, label
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
relief=gaussian_filter(z,13)
relief/=max(relief[land].max(),1)
surface=gaussian_filter((1-np.exp(-dist*5))*land*(350+relief*1050),7)
sy,sx=np.gradient(surface,20)
palettes={'N':(['#205e68','#438e94','#78bfc0','#c1e1df'],'#cedbdb','Glacial Turquoise'),'S':(['#493c39','#786052','#a48166','#d9be9b'],'#e2ddd3','Volcanic Ash')}
for edition,angle in [('N',0),('S',180)]:
    palette,background,mood=palettes[edition]
    sign=1 if edition=='N' else -1
    normal=np.sqrt(1+sx*sx+sy*sy)
    light=(math.sin(math.pi/4)+sign*math.cos(math.pi/4)*(sx+sy)/math.sqrt(2))/normal
    light=gaussian_filter(light,9)
    light=np.clip(.15+.85*light,0,1)
    shapes=[]
    def smooth_path(coords):
        # Rounded vector joins: midpoint quadratic curves retain broad sculptural facets.
        pts=coords[:-1] if coords[0]==coords[-1] else coords
        if len(pts)<3: return ''
        mid=lambda a,b: ((a[0]+b[0])/2,(a[1]+b[1])/2)
        fmt=lambda a:f'{a[0]:.2f},{a[1]:.2f}'
        return 'M '+fmt(mid(pts[-1],pts[0]))+' '+' '.join('Q '+fmt(v)+' '+fmt(mid(v,pts[(k+1)%len(pts)])) for k,v in enumerate(pts))+' Z'
    for idx,(level,color) in enumerate(zip([.35,.59,.79],palette[1:])):
        region=(light>level)&land
        labels,n=label(region)
        sizes=np.bincount(labels.ravel())
        keep=sizes>=220
        keep[0]=False
        mask=np.pad(keep[labels],1,constant_values=False)
        curves=[]
        for contour in find_contours(mask.astype(float),.5):
            if len(contour)<85: continue
            pts=approximate_polygon(contour,tolerance=2.8)
            if len(pts)<4: continue
            coords=[point(r-1,c-1) for r,c in pts]
            curves.append(smooth_path(coords))
        shapes.append(f'<path d="{" ".join(curves)}" fill="url(#shade{idx})" fill-rule="evenodd" transform="rotate({angle} 1024 1024)"/>')
    gradients="".join(f'<linearGradient id="shade{k}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="2048" y2="2048"><stop stop-color="{palette[k+1]}"/><stop offset="1" stop-color="{palette[k]}" stop-opacity=".32"/></linearGradient>' for k in range(3))
    svg=f'''<svg data-art-version="3.6" xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs>{gradients}<radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="{background}"/>
<g transform="translate(1024 1024) scale(1.13333333333333) translate(-1024 -1024)"><g clip-path="url(#coast)"><rect width="2048" height="2048" fill="{palette[0]}"/>{''.join(shapes)}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="{palette[0]}" stroke-width="8" stroke-linejoin="round"/></g>
</svg>'''
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':mood,'background':background,'palette':palette,'art_status':'experimental_draft','terrain_guided':True,'lighting':{'screen_direction':'upper_left','elevation_degrees':45,'shared_surface':True,'gradient_space':'screen_fixed'},'art_version':'3.6','artwork_extent_px':1740.8,'artwork_meters_per_pixel':mpp*75/85,'artwork_print_scale_denominator':mpp*75/85*300/0.0254,'surface_model':'DEM-led sculpted relief with screen-fixed tonal gradients'},indent=2))
