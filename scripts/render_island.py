"""Draft artwork renderer. Requires explicitly reviewed coastline metadata."""
import argparse, json, hashlib, random, math
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
import io

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
palette=['#145764','#278c99','#61c8c9','#afe5df','#edf7f5']
for edition,angle in [('N',0),('S',180)]:
    rng=random.Random(meta['id']+edition+'glacial-turquoise-v1')
    shapes=[]
    # Experimental organic bands; not a relief reconstruction.
    for i in range(10):
        y=120+i*210
        points=[(x,y+rng.uniform(-190,190)) for x in range(-300,2600,400)]
        curve=f'M {points[0][0]} {points[0][1]}'
        for (x0,y0),(x1,y1) in zip(points,points[1:]):
            mid=(x0+x1)/2
            curve+=f' C {mid} {y0}, {mid} {y1}, {x1} {y1}'
        curve+=' L 2600 2400 L -300 2400 Z'
        shapes.append(f'<path d="{curve}" fill="{palette[i%len(palette)]}" stroke="#101719" stroke-width="8" stroke-linejoin="round"/>')
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">
<defs><radialGradient id="bg"><stop stop-color="#173b48"/><stop offset="1" stop-color="#07131e"/></radialGradient><clipPath id="coast"><path d={d} clip-rule="evenodd" transform="rotate({angle} 1024 1024)"/></clipPath></defs>
<rect width="2048" height="2048" fill="url(#bg)"/>
<g clip-path="url(#coast)"><rect width="2048" height="2048" fill="{palette[0]}"/>{''.join(shapes)}</g>
<path d={d} transform="rotate({angle} 1024 1024)" fill="none" stroke="#080b0d" stroke-width="13" stroke-linejoin="round"/>
</svg>'''
    stem=a.output/(meta['id']+'-'+edition+'-draft')
    stem.with_suffix('.svg').write_text(svg)
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode())))
    image.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.json').write_text(json.dumps({**meta,'edition':edition,'orientation_degrees':angle,'color_mood':'Glacial Turquoise','art_status':'experimental_draft','terrain_guided':False},indent=2))
