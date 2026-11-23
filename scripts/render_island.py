"""Draft artwork renderer. Requires explicitly reviewed coastline metadata."""
import argparse, json, hashlib, random, math
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw
import io, base64
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt, label
from skimage.measure import find_contours, approximate_polygon

p=argparse.ArgumentParser()
p.add_argument('coastline',type=Path)
p.add_argument('metadata',type=Path)
p.add_argument('output',type=Path)
p.add_argument('--palette',choices=['bouvet','sicily'],default='bouvet')
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
resolution=float(tm.get('resolution_m',abs(tm['transform'][0])))
# Match Bouvet's *visual* smoothing in artwork space, not its 20 m DEM cells.
# Both islands are normalized to the same 1536px geographic footprint.
z=gaussian_filter(z,8)
gy,gx=np.gradient(z,resolution)
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
if land.sum()<1000:
    raise RuntimeError(f'Coastline rasterization produced only {land.sum()} land pixels')
print(f'Land mask: {land.sum():,} / {land.size:,} pixels')
coast_distance=gaussian_filter(distance_transform_edt(land),2)
dist=gaussian_filter(coast_distance,5)
dist/=max(dist.max(),1)
relief=gaussian_filter(z,13)
relief/=max(relief[land].max(),1)
surface=gaussian_filter((1-np.exp(-dist*5))*land*(350+relief*1050),7)
sy,sx=np.gradient(surface,20)
palettes={'N':(['#205e68','#438e94','#78bfc0','#c1e1df'],'#cedbdb','Glacial Turquoise'),'S':(['#493c39','#786052','#a48166','#d9be9b'],'#e2ddd3','Volcanic Ash')}
if a.palette=='sicily':
    palettes={'N':(['#65564a','#a58c71','#d2baa0','#f0e3cd'],'#e7e4d9','Mediterranean Limestone'),'S':(['#483c3c','#80564b','#bc8065','#e2b89a'],'#ddd3ca','Volcanic Terracotta')}
for edition,angle in [('N',0),('S',180)]:
    palette,background,mood=palettes[edition]
    sign=1 if edition=='N' else -1
    normal=np.sqrt(1+sx*sx+sy*sy)
    light=(math.sin(math.pi/4)+sign*math.cos(math.pi/4)*(sx+sy)/math.sqrt(2))/normal
    light=gaussian_filter(light,9)
    light=np.clip(.15+.85*light,0,1)
    # Continuous tonal field; eliminate hard polygon thresholds.
    # Soft Stone: narrow sculpted coastal bevel, without a second overlay or hard edge.
    # A fixed upper-left light interacts with the inward coast-distance gradient.
    edge_north,edge_east=np.gradient(coast_distance,20)
    edge_direction=(edge_east+edge_north)/math.sqrt(2)
    edge_sign=1 if edition=='N' else -1
    coastal_bevel=np.exp(-coast_distance/max(1,9/scale))
    soft_stone_light=light+0.105*edge_sign*edge_direction*coastal_bevel
    normalized=np.clip((soft_stone_light-.17)/.73,0,1)
    colors=np.array([[int(c[i:i+2],16) for i in (1,3,5)] for c in palette],dtype=float)
    position=normalized*3
    lo=np.minimum(np.floor(position).astype(int),2)
    fraction=(position-lo)[...,None]
    rgb=colors[lo]*(1-fraction)+colors[lo+1]*fraction
    rgba=np.concatenate([np.clip(rgb,0,255).astype(np.uint8),(land.astype(np.uint8)*255)[...,None]],axis=2)
    if np.ptp(rgb[land])<3:
        raise RuntimeError('Relief color field is nearly uniform: terrain rendering failed')
    rgba_img=Image.fromarray(rgba,'RGBA')
    if angle==180: rgba_img=rgba_img.rotate(180)
    buf=io.BytesIO()
    rgba_img.save(buf,format='PNG')
    embedded=base64.b64encode(buf.getvalue()).decode('ascii')
    xleft,ytop=point(0,0)
    xright,ybottom=point(h-1,w-1)
    image_x=min(xleft,xright)-abs(t[0]/mpp)/2
    image_y=min(ytop,ybottom)-abs(t[4]/mpp)/2
    image_width=abs(xright-xleft)+abs(t[0]/mpp)
    image_height=abs(ybottom-ytop)+abs(t[4]/mpp)
    if angle==180:
        image_x=2048-image_x-image_width
        image_y=2048-image_y-image_height
    tonal_image=f'<image x="{image_x:.3f}" y="{image_y:.3f}" width="{image_width:.3f}" height="{image_height:.3f}" preserveAspectRatio="none" href="data:image/png;base64,{embedded}"/>'
    svg=f'''<svg data-art-version="3.8" xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs><radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="{background}"/>
<g transform="translate(1024 1024) scale(1.13333333333333) translate(-1024 -1024)"><g clip-path="url(#coast)"><path d={d} transform="rotate({angle} 1024 1024)" fill="{palette[1]}"/>{tonal_image}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="{palette[0]}" stroke-width="3" stroke-linejoin="round"/></g>
</svg>'''
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':mood,'background':background,'palette':palette,'art_status':'experimental_draft','terrain_guided':True,'lighting':{'screen_direction':'upper_left','elevation_degrees':45,'shared_surface':True,'gradient_space':'continuous_terrain_raster'},'art_version':'3.8','artwork_extent_px':1740.8,'artwork_meters_per_pixel':mpp*75/85,'artwork_print_scale_denominator':mpp*75/85*300/0.0254,'surface_model':'Soft Stone: continuous DEM relief with directional coastal bevel','style_variant':'A – Soft Stone'},indent=2))
