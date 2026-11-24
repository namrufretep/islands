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
p.add_argument('--palette',choices=['bouvet','sicily','iceland','madagascar'],default='bouvet')
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
z=gaussian_filter(z,0.8 if a.palette in ('sicily','iceland','madagascar') else 8)
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
sy,sx=np.gradient(surface,resolution)
palettes={'N':(['#205e68','#438e94','#78bfc0','#c1e1df'],'#cedbdb','Glacial Turquoise'),'S':(['#493c39','#786052','#a48166','#d9be9b'],'#e2ddd3','Volcanic Ash')}
if a.palette in ('sicily','iceland','madagascar'):
    palettes={'N':(['#65564a','#a08059','#c8a67e','#f0e3cd'],'#e7e4d9','Mediterranean Limestone'),'S':(['#483c3c','#80564b','#bc8065','#e2b89a'],'#ddd3ca','Volcanic Terracotta')}
if a.palette=='iceland':
    palettes={'N':(['#30263f','#65547f','#a394c3','#e2d9ef'],'#ccd9cf','Arctic Amethyst'),'S':(['#382b29','#85523c','#c38a55','#e9c697'],'#243b49','Volcanic Copper')}
if a.palette=='madagascar':
    palettes={'N':(['#143d32','#34795c','#79b58b','#cce6b4'],'#dfb6b0','Emerald Jade'),'S':(['#172344','#354f91','#6989d0','#b9d1ef'],'#d5b56e','Imperial Lapis')}
version='4.3' if a.palette in ('sicily','iceland','madagascar') else '3.8'
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
    edge_north,edge_east=np.gradient(coast_distance,resolution)
    edge_direction=(edge_east+edge_north)/math.sqrt(2)
    edge_sign=1 if edition=='N' else -1
    coastal_bevel=np.exp(-coast_distance/9)
    soft_stone_light=light+0.105*edge_sign*edge_direction*coastal_bevel
    if a.palette in ('sicily','iceland','madagascar'):
        # v4.3: Bouvet-inspired convex sculpture in normalized artwork space.
        # Construct a broad rounded body, modulated by abstract elevation.
        px_per_cell=resolution/mpp
        sigma=max(1.0,52/px_per_cell)
        inward=distance_transform_edt(land)*px_per_cell
        rounded=1-np.exp(-inward/105)
        broad=gaussian_filter(z,sigma)
        low,high=np.percentile(broad[land],[3,99])
        elevation=np.clip((broad-low)/max(high-low,1),0,1)
        body=gaussian_filter(rounded*(0.38+0.62*elevation),max(1,26/px_per_cell))
        dy,dx=np.gradient(body,px_per_cell)
        dx*=220
        dy*=220
        hill=(math.sin(math.pi/4)+sign*math.cos(math.pi/4)*(dx+dy)/math.sqrt(2))/np.sqrt(1+dx*dx+dy*dy)
        soft_stone_light=gaussian_filter(.68*hill+.32*elevation,max(1,16/px_per_cell))
    # Normalize the sculptural light across each island's actual land pixels.
    # Retain Sicily's original palette, while restoring Bouvet-like tonal depth.
    shade_low,shade_high=np.percentile(soft_stone_light[land],[3,97])
    if shade_high-shade_low<0.025:
        raise RuntimeError('Insufficient relief contrast for Soft Stone artwork')
    normalized=np.clip((soft_stone_light-shade_low)/(shade_high-shade_low),0,1)
    normalized=normalized*normalized*(3-2*normalized)
    if a.palette in ('sicily','iceland','madagascar'):
        # Keep broad intermediate tones; avoid near-black/near-white hotspots.
        normalized=0.10+0.80*(0.55*normalized+0.45*np.clip((soft_stone_light-shade_low)/(shade_high-shade_low),0,1))
        normalized=gaussian_filter(normalized,max(.8,mpp/resolution*1.1))
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
    svg=f'''<svg data-art-version="{version}" xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs><radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="{background}"/>
<g transform="translate(1024 1024) scale(1.13333333333333) translate(-1024 -1024)"><g clip-path="url(#coast)"><path d={d} transform="rotate({angle} 1024 1024)" fill="{palette[1]}"/>{tonal_image}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="{palette[0]}" stroke-width="3" stroke-linejoin="round"/></g>
</svg>'''
    # Two optional art-direction studies. Keep the verified silhouette and
    # the original continuous terrain image unchanged.
    # A: dark gallery; C: atmospheric mineral, with a soft nonuniform field.
    # Two genuinely different art directions, including separate tonal artwork
    # (not merely a background recolor). Coastline and DEM stay identical.
    studies={
        'A': ('#111923','#34434b','#080e16',7),
        'C': ('#b6b2a8','#e1d6c3','#81949a',6),
    }
    for variant,(base_bg,inner_bg,outer_bg,coast_width) in studies.items():
        # Original terrain shading remains the source; modify only artistic tone.
        if variant=='A':
            # Bouvet-style light field: use the shared sculpted terrain surface
            # and directional light rather than Sicily's flattened elevation wash.
            # Normalize on land only; preserve nuanced shadows and highlights.
            bouvet_light=gaussian_filter(light + 0.055*edge_sign*
                edge_direction*np.exp(-coast_distance/12),12)
            low,high=np.percentile(bouvet_light[land],[4,96])
            if high-low<0.015:
                raise RuntimeError('Gallery study lacks directional light variation')
            bouvet_tone=np.clip((bouvet_light-low)/(high-low),0,1)
            # Blend broad light with finer natural transitions; no hard 3D facets.
            variant_tone=0.08+0.84*gaussian_filter(bouvet_tone,6)
        else:
            # Atmospheric mineral: fine overlapping tonal washes, airy midtones.
            fine=gaussian_filter(normalized,4)
            broadwash=gaussian_filter(normalized,30)
            variant_tone=np.clip(0.20+0.54*broadwash+0.17*(fine-broadwash),0,1)
            variant_tone=gaussian_filter(variant_tone,6)
        variant_position=variant_tone*3
        variant_lo=np.minimum(np.floor(variant_position).astype(int),2)
        variant_frac=(variant_position-variant_lo)[...,None]
        variant_rgb=colors[variant_lo]*(1-variant_frac)+colors[variant_lo+1]*variant_frac
        if variant=='A':
            # Slightly deepen the shadow without introducing sharp 3D facets.
            variant_rgb=np.clip(variant_rgb*0.96,0,255)
        variant_rgba=np.concatenate([variant_rgb.astype(np.uint8),
                        (land.astype(np.uint8)*255)[...,None]],axis=2)
        variant_img=Image.fromarray(variant_rgba,'RGBA')
        if angle==180: variant_img=variant_img.rotate(180)
        variant_buf=io.BytesIO()
        variant_img.save(variant_buf,format='PNG')
        variant_embedded=base64.b64encode(variant_buf.getvalue()).decode('ascii')
        variant_image=tonal_image.replace(embedded,variant_embedded)
        gradient=(f'<defs><radialGradient id="studio-background" cx="36%" cy="28%" r="83%">'
                  f'<stop offset="0" stop-color="{inner_bg}"/>'
                  f'<stop offset="0.62" stop-color="{base_bg}"/>'
                  f'<stop offset="1" stop-color="{outer_bg}"/>'
                  f'</radialGradient></defs>')
        artwork=svg.replace('<rect width="2048" height="2048" fill="'+background+'"/>',
                            gradient+'<rect width="2048" height="2048" fill="url(#studio-background)"/>')
        artwork=artwork.replace(tonal_image,variant_image)
        artwork=artwork.replace('stroke-width="3" stroke-linejoin="round"',
                                f'stroke-width="{coast_width}" stroke-linejoin="round"')
        variant_stem=a.output/(meta['id']+'-'+edition+'-'+variant+'-study')
        variant_stem.with_suffix('.svg').write_text(artwork)
        variant_stem.with_suffix('.json').write_text(json.dumps({
            'id':meta['id'],'edition':edition,'variant':variant,
            'status':'experimental_style_study','palette':palette,
            'background_direction':'Dark Gallery' if variant=='A' else 'Atmospheric Stone',
            'coastline_stroke_px':coast_width,
            'source':'verified coastline and DEM; independent art-direction tonal field'
        },indent=2))
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':mood,'background':background,'palette':palette,'art_status':'experimental_draft','terrain_guided':True,'lighting':{'screen_direction':'upper_left','elevation_degrees':45,'shared_surface':True,'gradient_space':'continuous_terrain_raster'},'art_version':version,'artwork_extent_px':1740.8,'artwork_meters_per_pixel':mpp*75/85,'artwork_print_scale_denominator':mpp*75/85*300/0.0254,'surface_model':'Soft Stone: convex mineral sculpture with continuous broad volumes and balanced midtones' if a.palette in ('sicily','iceland','madagascar') else 'Soft Stone: continuous DEM relief with directional coastal bevel','style_variant':'A – Soft Stone'},indent=2))
